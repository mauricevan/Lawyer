"""Format and sanitize layperson answer text."""
import re

_CELEX_PATTERN = re.compile(r"\b320\d{2}[RL]\d{4}\b", re.IGNORECASE)
_CELEX_LABEL = re.compile(r"CELEX:\s*\S+", re.IGNORECASE)
_CHUNK_HEADER = re.compile(r"\[Bron \d+\][^\n]*\n?", re.IGNORECASE)
_NAV_NOISE = re.compile(
    r"skip to main content|my eur-lex|http://publications\.|eur-lex -|"
    r"eur-lex celex|eu/resource/cellar/",
    re.IGNORECASE,
)
_WEAK_ARTICLE = re.compile(r"lijkt artikel\s+[\w() ]+\s*relevant", re.IGNORECASE)
_TITLE_JUNK = re.compile(r"de regels over\s*-|\b-\s*nl\b", re.IGNORECASE)
_PREAMBLE = re.compile(
    r"gezien het voorstel van de commissie|having regard to the proposal|"
    r"considering that|whereas|this directive shall",
    re.IGNORECASE,
)
_ARTICLE_PIPE = re.compile(r"\|\s*article\s*\|", re.IGNORECASE)
_ARTICLE_PIPE_MIX = re.compile(r"artikel \d+ \| article", re.IGNORECASE)
_DIRECT_KORT = re.compile(
    r"\b(ja|nee|wel|niet|recht op|mag|moet|minimaal|maximaal|ten minste|meestal|soms|verplicht|geldt|€|\d)",
    re.IGNORECASE,
)
_WEAK_PHRASES = (
    "kan dit niet bevestigen",
    "kan niet bevestigen",
    "geen informatie",
    "lijkt artikel",
    "skip to main content",
    "eur-lex celex",
    "eu/resource/cellar",
    "zijn relevant voor uw vraag",
    "zijn hier relevant",
    "de regels over -",
    "gezien het voorstel van de commissie",
    "having regard to the proposal",
    "this directive shall",
    "deze richtlijn shall",
    "after transmission of the draft",
    "article 114 thereof",
    "from the european commission",
    "paragraph\navis",
    "| article |",
    "| body",
    ".xml",
    "| section",
    "section .",
    "artikel —",
    "artikel -:",
)


def strip_hybrid_tables(text: str) -> str:
    """Remove pipe-table metadata dumps from LLM/hybrid answers."""
    cleaned_lines = []
    for line in (text or "").splitlines():
        if _ARTICLE_PIPE.search(line) or _ARTICLE_PIPE_MIX.search(line):
            continue
        if re.search(r"^\|\s*\w", line) and "Verplichting" not in line:
            continue
        cleaned_lines.append(line)
    return re.sub(r"\n{3,}", "\n\n", "\n".join(cleaned_lines)).strip()


def strip_technical_noise(text: str) -> str:
    """Remove CELEX codes, chunk headers, navigation, and artikel None."""
    cleaned = text or ""
    cleaned = _CELEX_LABEL.sub("", cleaned)
    cleaned = _CELEX_PATTERN.sub("", cleaned)
    cleaned = _CHUNK_HEADER.sub("", cleaned)
    cleaned = _NAV_NOISE.sub("", cleaned)
    cleaned = _PREAMBLE.sub("", cleaned)
    cleaned = strip_hybrid_tables(cleaned)
    cleaned = re.sub(r"\bartikel\s+None\b", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"[ \t]{2,}", " ", cleaned)
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)
    return cleaned.strip()


def has_required_sections(text: str) -> bool:
    """Return True when canonical layperson sections are present."""
    if "## Kort antwoord" not in text:
        return False
    if "## Wat betekent dit in de praktijk?" in text:
        return True
    return "## Uitleg" in text


def is_clear_layperson_format(text: str) -> bool:
    """True when answer uses the antwoord-eerst section layout."""
    body = text or ""
    return (
        "## Kort antwoord" in body
        and "## Wat betekent dit in de praktijk?" in body
        and "## Voorbeeld" in body
        and "## Juridische basis" in body
    )


def ensure_layperson_sections(text: str, question: str) -> str:
    """Add missing layperson sections or restructure plain text."""
    body = strip_technical_noise(text)
    if is_clear_layperson_format(body) and not is_weak_layperson_answer(body):
        return _append_tail_sections(body, question)
    if has_required_sections(body) and not is_weak_layperson_answer(body):
        return _append_tail_sections(body, question)
    body = _extract_section_body(body, "Uitleg") or _extract_section_body(body, "Kort antwoord") or body
    body = body.strip() or "Ik kan op basis van deze bronnen geen helder antwoord geven."
    kort = _first_sentence(body, max_len=280)
    uitleg = body[:900]
    return (
        f"## Kort antwoord\n{kort}\n\n"
        f"## Wat betekent dit in de praktijk?\n"
        f"| Verplichting | Uitleg |\n| --- | --- |\n| Kernregel | {uitleg[:400]} |\n\n"
        f"## Voorbeeld\n{_example_hint(question)}\n\n"
        f"## Juridische basis\n- {uitleg[:320]}\n\n"
        f"## Let op\nDit is geen persoonlijk juridisch advies."
    )


def _append_tail_sections(body: str, question: str) -> str:
    if "## Wat betekent dit in de praktijk?" not in body and "## Uitleg" in body:
        uitleg = _extract_section_body(body, "Uitleg")
        body = body.replace(
            "## Uitleg",
            "## Wat betekent dit in de praktijk?\n| Verplichting | Uitleg |\n| --- | --- |\n"
            f"| Kernregel | {uitleg[:400]} |\n\n## Uitleg",
            1,
        )
    if "## Wat dit voor u kan betekenen" not in body and "## Voorbeeld" not in body:
        body = f"{body.rstrip()}\n\n## Voorbeeld\n{_example_hint(question)}"
    if "## Let op" not in body:
        body = f"{body.rstrip()}\n\n## Let op\nDit is geen persoonlijk juridisch advies."
    return body


def _extract_section_body(text: str, section: str) -> str:
    pattern = rf"##\s*{re.escape(section)}\s*\n(.*?)(?=\n##\s|\Z)"
    match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
    return match.group(1).strip() if match else ""


def _first_sentence(text: str, max_len: int = 280) -> str:
    cleaned = re.sub(r"\s+", " ", text).strip()
    for part in re.split(r"(?<=[.!?])\s+", cleaned):
        if len(part.strip()) > 40:
            return part.strip()[:max_len]
    return cleaned[:max_len]


def is_hybrid_boilerplate(text: str) -> bool:
    """True when LLM/hybrid output contains metadata dumps or broken structure."""
    body = text or ""
    lowered = body.lower()
    boilerplate_phrases = (
        "zijn relevant voor uw vraag",
        "zijn hier relevant",
        "de regels over -",
        "gezien het voorstel van de commissie",
        "having regard to the proposal",
        "this directive shall",
        "skip to main content",
        "lijkt artikel",
        "| article |",
        "| body",
        ".xml",
    )
    if any(p in lowered for p in boilerplate_phrases):
        return True
    if body.count("## Kort antwoord") > 1:
        return True
    if _ARTICLE_PIPE.search(body) or _ARTICLE_PIPE_MIX.search(body):
        return True
    if _PREAMBLE.search(body) or _TITLE_JUNK.search(body):
        return True
    return False


def is_weak_layperson_answer(text: str) -> bool:
    """True when answer avoids the question or contains boilerplate."""
    body = text or ""
    lowered = body.lower()
    if len(body) < 120:
        return True
    if any(phrase in lowered for phrase in _WEAK_PHRASES):
        return True
    if _WEAK_ARTICLE.search(body) or _TITLE_JUNK.search(body) or _PREAMBLE.search(body):
        return True
    if body.count("## Kort antwoord") > 1:
        return True
    if _ARTICLE_PIPE.search(body) or _ARTICLE_PIPE_MIX.search(body):
        return True
    if _CELEX_PATTERN.search(body):
        return True
    if not has_required_sections(body):
        return True
    return not _has_direct_kort_antwoord(body)


def replace_fallback_boilerplate(text: str) -> str:
    """Strip weak LLM fallback phrases without replacing with other boilerplate."""
    cleaned = _WEAK_ARTICLE.sub("", text or "")
    cleaned = re.sub(
        r"Op basis of [^\n]+ lijkt (?:deze regeling|artikel [^\n]+) relevant[^\n]*",
        "",
        cleaned,
        flags=re.IGNORECASE,
    )
    cleaned = re.sub(
        r"De regels over [^\n]+ zijn (?:hier )?relevant[^\n]*",
        "",
        cleaned,
        flags=re.IGNORECASE,
    )
    return cleaned.strip()


def excerpt_is_usable(excerpt: str) -> bool:
    """Return False when chunk excerpt is metadata or legal preamble."""
    return bool(excerpt.strip()) and not is_weak_layperson_answer(excerpt)


def _has_direct_kort_antwoord(text: str) -> bool:
    kort = _kort_section(text)
    if re.match(r"^\s*(deze richtlijn|artikel \d+|this directive|market surveillance)\b", kort, re.IGNORECASE):
        return False
    if re.search(r"\bshall take appropriate measures\b", kort, re.IGNORECASE):
        return False
    return bool(_DIRECT_KORT.search(kort))


def _kort_section(text: str) -> str:
    for marker in (
        "## Wat betekent dit in de praktijk?",
        "## Uitleg",
        "## Voorbeeld",
        "## Juridische basis",
    ):
        if marker in text:
            return text.split(marker)[0]
    return text[:400]


def _example_hint(question: str) -> str:
    lowered = question.lower()
    if "exploitant" in lowered or "milieuschade" in lowered:
        return (
            "Een bedrijf veroorzaakt per ongeluk milieuschade. De exploitant moet direct "
            "maatregelen nemen, melden en herstellen."
        )
    return _practical_hint(question)


def _practical_hint(question: str) -> str:
    lowered = question.lower()
    if "werkgever" in lowered or "privacy" in lowered:
        return "Controleer welke informatie uw werkgever mag verwerken en vraag om uitleg in begrijpelijke taal."
    if "vlucht" in lowered or "vertraging" in lowered:
        return "Bewaar tickets en communicatie; dien een claim in bij de luchtvaartmaatschappij."
    if "fabrikant" in lowered or "product" in lowered or "veiligheid" in lowered:
        return (
            "Meld een veiligheidsrisico tijdig aan de bevoegde autoriteit en documenteer "
            "welke corrigerende maatregelen u neemt."
        )
    return "Noteer feiten en data; zoek hulp bij de genoemde instantie als u twijfelt."

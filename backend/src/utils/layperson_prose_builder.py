"""Human-readable Dutch layperson sections from operative legal excerpts."""
import re

from backend.src.utils.defined_term_extractor import extract_defined_term, is_definition_style_question
from backend.src.utils.layperson_answer_formatter import _practical_hint

_XML_OR_PIPE = re.compile(r"\.xml|\s\|\s|\| section", re.I)
_RECITAL_START = re.compile(r"^\(\d+\)\s")
_BAD_PHRASES = (
    "together with the adaptation",
    "in the absence of european standards",
    "having regard to",
    "after transmission of the draft",
    "section .",
)


def build_layperson_sections(question: str, excerpts: list[dict[str, str]]) -> str | None:
    """Return full markdown answer or None when excerpts are not usable."""
    kort = _build_kort_antwoord(question, excerpts)
    uitleg = _build_uitleg(excerpts, question)
    if not kort or not uitleg:
        return None
    return (
        f"## Kort antwoord\n{kort}\n\n"
        f"## Uitleg\n{uitleg}\n\n"
        f"## Wat dit voor u kan betekenen\n{_practical_hint(question)}\n\n"
        f"## Let op\nDit is geen persoonlijk juridisch advies. Raadpleeg een jurist bij twijfel."
    )


def _build_kort_antwoord(question: str, excerpts: list[dict[str, str]]) -> str | None:
    defined = extract_defined_term(question).term
    if defined and is_definition_style_question(question):
        definition = _definition_lead(excerpts, defined)
        if definition:
            return (
                f"Ja. In de Europese wetgeving wordt «{defined}» als volgt gedefinieerd: "
                f"{definition}"
            )
    sentences = _collect_sentences(excerpts, max_count=5, question=question)
    lowered_q = question.lower()
    if not (defined and is_definition_style_question(question)):
        if "fabrikant" in lowered_q:
            about_manufacturer = [s for s in sentences if _is_about_manufacturer(s)]
            if about_manufacturer:
                sentences = about_manufacturer
        if "exploitant" in lowered_q:
            about_operator = [s for s in sentences if _is_about_operator(s)]
            if about_operator:
                sentences = about_operator
        if any(word in lowered_q for word in ("platform", "contentwebsite", "marktplaats", "website")):
            about_platform = [s for s in sentences if _is_about_platform(s)]
            if about_platform:
                sentences = about_platform
        if any(word in lowered_q for word in ("terugroep", "terughaal", "recall", "veiligheidsrisico")):
            about_recall = [s for s in sentences if "terugroep" in s.lower()]
            if about_recall:
                sentences = about_recall
        if any(word in lowered_q for word in ("douane", "invoer", "import", "china", "etsy", "pakket")):
            about_customs = [s for s in sentences if _is_about_customs_declaration(s)]
            if about_customs:
                sentences = about_customs
    sentences = sentences[:3]
    if not sentences:
        return None
    intro = _intro_for_question(question)
    body = _join_sentences(sentences, max_len=520)
    return f"{intro} {body}".strip()


def _build_uitleg(excerpts: list[dict[str, str]], question: str = "") -> str | None:
    defined = extract_defined_term(question or "").term
    is_definition = bool(defined and is_definition_style_question(question or ""))
    blocks: list[str] = []
    for item in excerpts[:3]:
        article = str(item.get("article", "")).strip()
        if not article or article in {"—", "?", "-"}:
            continue
        regulation = item.get("regulation", "de EU-regelgeving")
        sentences = _extract_sentences(str(item.get("text", "")), max_count=6)
        if is_definition and defined:
            definition_sentences = [s for s in sentences if _sentence_defines_term(s, defined)]
            if definition_sentences:
                sentences = definition_sentences
        elif "fabrikant" in (question or "").lower():
            manufacturer_sentences = [s for s in sentences if _is_about_manufacturer(s)]
            if manufacturer_sentences:
                sentences = manufacturer_sentences
        if "exploitant" in (question or "").lower():
            operator_sentences = [s for s in sentences if _is_about_operator(s)]
            if operator_sentences:
                sentences = operator_sentences
        if not sentences:
            continue
        body = _join_sentences(sentences, max_len=800)
        heading = f"**Artikel {article}** ({regulation})" if article != "algemeen" else f"**{regulation}**"
        blocks.append(f"{heading}\n\n{body}")
    return "\n\n".join(blocks) if blocks else None


def _intro_for_question(question: str) -> str:
    lowered = question.lower()
    if "exploitant" in lowered and "milieuschade" in lowered:
        return "Exploitanten die milieuschade veroorzaken, moeten onder meer het volgende:"
    if "fabrikant" in lowered and ("risico" in lowered or "veilig" in lowered):
        return "Als fabrikant moet u bij een veiligheidsrisico onder meer het volgende:"
    if "fabrikant" in lowered:
        return "Voor fabrikanten gelden onder meer deze verplichtingen:"
    if any(word in lowered for word in ("platform", "contentwebsite", "marktplaats", "website")):
        return "Als u een online platform of contentwebsite wilt starten, gelden onder DSA onder meer:"
    if any(word in lowered for word in ("legitim", "identif", "paspoort", "eidas")):
        return (
            "Deels EU, deels nationaal: voor vrij verkeer en elektronische identificatie bij "
            "(overheids)diensten gelden onder meer de volgende EU-regels:"
        )
    if any(word in lowered for word in ("terugroep", "terughaal", "recall", "veiligheidsrisico")):
        return (
            "Als verkoper of fabrikant moet u een onveilig product terugroepen wanneer de EU-regels "
            "dat vereisen. In het kort:"
        )
    if any(word in lowered for word in ("lidstaten", "douanegebied", "douane-unie", "douaneunie")):
        return (
            "Het douane-uniegebied van de EU wordt in het douanewetboek en het Verdrag beschreven. "
            "In het kort:"
        )
    if any(word in lowered for word in ("douane", "invoer", "import", "china", "etsy", "pakket")):
        return (
            "Voor invoer van goederen in de EU gelden douaneprocedures; kleine zendingen betekenen "
            "niet automatisch dat geen aangifte nodig is. In het kort:"
        )
    return "Op basis van de EU-regelgeving die voor uw vraag geldt:"


def _collect_sentences(excerpts: list[dict[str, str]], max_count: int, question: str = "") -> list[str]:
    from backend.src.utils.legal_chunk_text import score_chunk_relevance

    candidates: list[tuple[int, str]] = []
    seen: set[str] = set()
    for item in excerpts:
        for sentence in _extract_sentences(str(item.get("text", "")), max_count=12):
            if sentence in seen:
                continue
            seen.add(sentence)
            rank = score_chunk_relevance(sentence, question) if question else 0
            candidates.append((rank, sentence))
    candidates.sort(key=lambda pair: pair[0], reverse=True)
    return [sentence for _, sentence in candidates[:max_count]]


def _extract_sentences(text: str, max_count: int) -> list[str]:
    from backend.src.utils.legal_chunk_text import clean_chunk_text

    cleaned = re.sub(r"\s+", " ", clean_chunk_text(text or "")).strip()
    if not cleaned:
        return []
    parts = re.split(r"(?<=[.!?])\s+", cleaned)
    return [part.strip() for part in parts if _is_usable_sentence(part)][:max_count]


def _is_about_customs_declaration(sentence: str) -> bool:
    lowered = sentence.lower()
    if any(marker in lowered for marker in (
        "uitvoerrechten", "terugbetaling", "douanekantoor van uitvoer",
        "ongeldig worden gemaakt", "commissie gelast",
    )):
        return False
    return any(marker in lowered for marker in (
        "aangifte", "vrijmaking", "vrije verkeer", "douanewetboek",
        "douanerechten", "toepassingsgebied", "goederen die de douane",
    ))


def _is_about_platform(sentence: str) -> bool:
    lowered = sentence.lower()
    if any(marker in lowered for marker in (
        "commissie gelast", "lidstaten zorgen", "markttoezichtautoriteit",
        "krachtens lid 1 vast te stellen",
    )):
        return False
    return any(marker in lowered for marker in (
        "platform", "hosting", "tussenhandel", "intermediary",
        "dienstaanbieder", "online", "website", "publisher",
        "informatiemaatschappij", "opslag", "content",
    ))


def _is_about_operator(sentence: str) -> bool:
    lowered = sentence.lower()
    if re.search(r"\ba\)\s", lowered):
        return False
    if lowered.startswith(("de bevoegde instantie", "de lidstaat", "lidstaten", "artikel 5, leden")):
        return False
    return "exploitant" in lowered


def _is_about_manufacturer(sentence: str) -> bool:
    lowered = sentence.lower()
    if re.search(r"\ba\)\s", lowered):
        return False
    if lowered.startswith(("het mandaat", "een gemachtigde", "de gemachtigde")):
        return False
    if lowered.startswith("importeur") or lowered.startswith("importeurs"):
        return False
    return "fabrikant" in lowered


def _is_usable_sentence(sentence: str) -> bool:
    if len(sentence) < 45:
        return False
    if _XML_OR_PIPE.search(sentence) or _RECITAL_START.match(sentence.strip()):
        return False
    lowered = sentence.lower()
    if lowered.startswith(("indien dit ", "waarbij ", "tenzij ")):
        return False
    return not any(phrase in lowered for phrase in _BAD_PHRASES)


def _join_sentences(sentences: list[str], max_len: int) -> str:
    merged = " ".join(sentences)
    if len(merged) <= max_len:
        return merged
    cut = merged[:max_len]
    last_period = cut.rfind(". ")
    if last_period > 100:
        return cut[: last_period + 1]
    return cut.rstrip() + "…"


def _definition_lead(excerpts: list[dict[str, str]], term: str) -> str | None:
    for item in excerpts:
        for sentence in _extract_sentences(str(item.get("text", "")), max_count=20):
            if _sentence_defines_term(sentence, term):
                return _cleanup_definition_sentence(sentence, term)
    return None


def _sentence_defines_term(sentence: str, term: str) -> bool:
    lowered = sentence.lower()
    if term not in lowered:
        return False
    if any(marker in lowered for marker in ("wordt verstaan", "verstaan onder", "definities")):
        return True
    return bool(re.search(rf'\d+\)\s*[""\'\u201c\u201d\u201e]{re.escape(term)}', sentence, re.I))


def _cleanup_definition_sentence(sentence: str, term: str) -> str:
    match = re.search(
        rf'(\d+\)\s*)?[""\'\u201c\u201d\u201e]{re.escape(term)}[""\'\u201c\u201d\u201e:]?',
        sentence,
        re.I,
    )
    if match:
        return sentence[match.start():].strip()
    return sentence.strip()

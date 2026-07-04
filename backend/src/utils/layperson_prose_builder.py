"""Human-readable Dutch layperson sections from operative legal excerpts."""
import re

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
    sentences = _collect_sentences(excerpts, max_count=5, question=question)
    lowered_q = question.lower()
    if "fabrikant" in lowered_q:
        about_manufacturer = [s for s in sentences if _is_about_manufacturer(s)]
        if about_manufacturer:
            sentences = about_manufacturer
    if "exploitant" in lowered_q:
        about_operator = [s for s in sentences if _is_about_operator(s)]
        if about_operator:
            sentences = about_operator
    sentences = sentences[:3]
    if not sentences:
        return None
    intro = _intro_for_question(question)
    body = _join_sentences(sentences, max_len=520)
    return f"{intro} {body}".strip()


def _build_uitleg(excerpts: list[dict[str, str]], question: str = "") -> str | None:
    blocks: list[str] = []
    for item in excerpts[:3]:
        article = str(item.get("article", "")).strip()
        if not article or article in {"—", "?", "-"}:
            continue
        regulation = item.get("regulation", "de EU-regelgeving")
        sentences = _extract_sentences(str(item.get("text", "")), max_count=6)
        if "fabrikant" in (question or "").lower():
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

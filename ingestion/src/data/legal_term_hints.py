"""CELEX hint map derived from curated corpus metadata."""
import re

from ingestion.src.data.curated_loader import load_curated_documents

STATIC_HINTS: dict[str, str] = {
    "dora": "32022R2554",
    "digitale operationele weerbaarheid": "32022R2554",
    "csrd": "32022L2464",
    "duurzaamheidsrapportering": "32022L2464",
    "gdpr": "32016R0679",
    "avg": "32016R0679",
    "ai act": "32024R1689",
    "kunstmatige intelligentie": "32024R1689",
    "transparante arbeidsvoorwaarden": "32019L1152",
    "consumer cooperation": "32017R2394",
    "consumentenautoriteiten": "32017R2394",
}


def build_legal_term_celex_hints() -> dict[str, str]:
    """Build hint -> CELEX map from curated short titles and static aliases."""
    hints = dict(STATIC_HINTS)
    for document in load_curated_documents():
        if document.short_title:
            hints[document.short_title.lower().strip()] = document.celex
        label = _normalize_label(document.title)
        if label and label not in hints:
            hints[label] = document.celex
    return hints


def match_celex_hints(question: str, hints: dict[str, str] | None = None) -> set[str]:
    """Return CELEX codes whose hints appear in the question (longest match first)."""
    source = hints or build_legal_term_celex_hints()
    query_lower = question.lower()
    matched: set[str] = set()
    for hint in sorted(source.keys(), key=len, reverse=True):
        if hint in query_lower:
            matched.add(source[hint])
    celex_match = re.search(r"\b\d{5}[A-Z]\d{4}\b", question.upper())
    if celex_match:
        matched.add(celex_match.group(0))
    return matched


def match_primary_celex_hint(question: str, hints: dict[str, str] | None = None) -> str | None:
    """Return the first CELEX from longest matching hint."""
    source = hints or build_legal_term_celex_hints()
    query_lower = question.lower()
    for hint in sorted(source.keys(), key=len, reverse=True):
        if hint in query_lower:
            return source[hint]
    celex_match = re.search(r"\b\d{5}[A-Z]\d{4}\b", question.upper())
    return celex_match.group(0) if celex_match else None


def _normalize_label(title: str) -> str:
    cleaned = re.sub(r"\([^)]*\)", "", title).strip().lower()
    for prefix in ("verordening ", "richtlijn ", "besluit "):
        if cleaned.startswith(prefix):
            cleaned = cleaned[len(prefix):]
    return cleaned[:120].strip()

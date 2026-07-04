"""Re-rank legal chunks by actor/issue fit — role-based, domain-agnostic."""
from typing import Any

from backend.src.utils.legal_chunk_text import clean_chunk_text
from backend.src.utils.legal_question_interpretation import LegalActor, LegalIssue

_PRIVATE_ACTORS = frozenset({"manufacturer", "consumer", "operator", "employee"})
_AUTHORITY_MARKERS = (
    "market surveillance authorit",
    "markttoezichtautoriteit",
    "bevoegde autoriteit",
    "member states shall ensure",
    "lidstaten zorgen ervoor",
    "competent authorit",
    "customs authorities",
    "douaneautoriteit",
)
_ENFORCEMENT_MARKERS = (
    "enforcement", "handhaving", "sanction", "sanctie", "prohibit the placing",
    "verbod op het in de handel brengen", "withdrawal order", "market surveillance",
)
_PRIVATE_PARTY_MARKERS = (
    "fabrikant", "manufacturer", "economic operator", "importeur", "distributeur",
    "producent", "consument", "consumer", "exploitant", "operator", "verkoper",
    "werknemer", "employee", "worker", "medewerker",
)
_ACCESS_MARKERS = (
    "conformity", "conformiteit", "conformiteitsverklaring", "harmonisation legislation",
    "harmonisatiewetgeving", "placing on the market", "op de markt brengen",
    "technical documentation", "technische documentatie", "ce marking", "ce-markering",
)
_OBLIGATION_MARKERS = ("shall", "must", "verplicht", "moet", "is required")
_RIGHTS_MARKERS = (
    "right to", "recht op", "rechten van", "passenger rights", "passagier",
    "non-discrimination", "discriminatie", "gelijke behandeling",
)
_PRIVATE_NON_ENFORCEMENT_ISSUES = frozenset({
    "market_access", "obligation", "definition", "rights",
})


def score_chunk_for_context(text: str, actor: LegalActor, issue: LegalIssue) -> int:
    """Higher score = better fit (+2 match, -3 wrong role/enforcement noise)."""
    lowered = clean_chunk_text(text).lower()
    score = 0
    if actor in _PRIVATE_ACTORS and _mentions_private_party(lowered):
        score += 2
    if actor == "authority" and _contains_any(lowered, _AUTHORITY_MARKERS):
        score += 2
    if issue == "market_access" and _contains_any(lowered, _ACCESS_MARKERS):
        score += 2
    if issue == "obligation" and _contains_any(lowered, _OBLIGATION_MARKERS):
        score += 2
    if issue == "rights" and _contains_any(lowered, _RIGHTS_MARKERS):
        score += 2
    if issue == "enforcement" and _contains_any(lowered, _ENFORCEMENT_MARKERS + _AUTHORITY_MARKERS):
        score += 2
    if actor in _PRIVATE_ACTORS and issue != "enforcement":
        if _contains_any(lowered, _AUTHORITY_MARKERS):
            score -= 3
        if issue in _PRIVATE_NON_ENFORCEMENT_ISSUES and _contains_any(lowered, _ENFORCEMENT_MARKERS):
            score -= 3
    return score


def rank_chunks_by_legal_context(
    chunks: list[dict[str, Any]],
    actor: LegalActor,
    issue: LegalIssue,
) -> list[dict[str, Any]]:
    """Sort chunks by actor/issue score descending."""
    if actor == "unknown" and issue == "unknown":
        return list(chunks)
    scored = [
        (score_chunk_for_context(str(chunk.get("text", "")), actor, issue), chunk)
        for chunk in chunks
    ]
    scored.sort(key=lambda pair: pair[0], reverse=True)
    return [chunk for _, chunk in scored]


def filter_chunks_for_retry(
    chunks: list[dict[str, Any]],
    actor: LegalActor,
    issue: LegalIssue,
) -> list[dict[str, Any]]:
    """Drop authority/enforcement-heavy chunks when regenerating private-party answers."""
    if actor not in _PRIVATE_ACTORS or issue == "enforcement":
        return list(chunks)
    kept = [
        chunk for chunk in chunks
        if score_chunk_for_context(str(chunk.get("text", "")), actor, issue) >= 0
    ]
    return kept or list(chunks)


def _mentions_private_party(text: str) -> bool:
    return _contains_any(text, _PRIVATE_PARTY_MARKERS)


def _contains_any(text: str, markers: tuple[str, ...]) -> bool:
    return any(marker in text for marker in markers)

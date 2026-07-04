"""Rank EUR-Lex chunks by legal_question_type — generic, domain-agnostic."""
from typing import Any

from backend.src.utils.legal_question_type_inference import LegalQuestionType

_ENFORCEMENT_MARKERS = (
    "markttoezichtautoriteit", "market surveillance", "non-conform", "non conform",
    "van de markt", "withdrawal", "terugroep", "artikel 28", "corrective action",
)
_ENFORCEMENT_NOISE = (
    "douaneautoriteit", "douaneregeling", "informatie- en communicatiesysteem",
    "invoerrechten", "customs authorities",
)
_MARKET_ACCESS_MARKERS = (
    "ce-mark", "ce marking", "conformiteit", "conformity", "op de markt brengen",
    "placing on the market", "harmonisatiewetgeving", "technische documentatie",
)
_NATIONAL_MEASURE_MARKERS = (
    "lidstaat", "lidstaten", "nationale maatregel", "afwijken", "derogation",
    "harmonisatie", "mutual recognition", "wederzijdse erkenning",
)
_RIGHTS_MARKERS = (
    "recht op", "rechten", "herroep", "discriminatie", "gelijke behandeling",
)


def rank_chunk_for_question_type(text: str, question_type: LegalQuestionType) -> int:
    """Higher score = better fit for the interpreted question type."""
    if question_type == "unknown":
        return 0
    lowered = (text or "").lower()
    score = 0
    if question_type == "enforcement":
        score += 2 * sum(1 for m in _ENFORCEMENT_MARKERS if m in lowered)
        score -= 3 * sum(1 for m in _ENFORCEMENT_NOISE if m in lowered)
    if question_type == "market_access":
        score += 2 * sum(1 for m in _MARKET_ACCESS_MARKERS if m in lowered)
        score -= 3 if any(m in lowered for m in _ENFORCEMENT_NOISE) else 0
    if question_type == "national_measure":
        score += 2 * sum(1 for m in _NATIONAL_MEASURE_MARKERS if m in lowered)
        score -= 3 if any(m in lowered for m in _ENFORCEMENT_NOISE) else 0
    if question_type in {"rights", "obligations"}:
        score += 2 * sum(1 for m in _RIGHTS_MARKERS if m in lowered)
    return score


def rank_chunks_by_question_type(
    chunks: list[dict[str, Any]],
    question_type: LegalQuestionType,
) -> list[dict[str, Any]]:
    """Sort chunks by question-type relevance."""
    if question_type == "unknown" or not chunks:
        return list(chunks)
    scored = [
        (rank_chunk_for_question_type(str(chunk.get("text", "")), question_type), chunk)
        for chunk in chunks
    ]
    scored.sort(key=lambda pair: pair[0], reverse=True)
    return [chunk for _, chunk in scored]


def filter_chunks_for_question_type_retry(
    chunks: list[dict[str, Any]],
    question_type: LegalQuestionType,
) -> list[dict[str, Any]]:
    """Drop low-scoring chunks when regenerating answers."""
    if question_type == "unknown":
        return list(chunks)
    kept = [
        chunk for chunk in chunks
        if rank_chunk_for_question_type(str(chunk.get("text", "")), question_type) >= 0
    ]
    return kept or list(chunks)

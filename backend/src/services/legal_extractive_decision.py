"""Decide when extractive answers better fulfill the product promise."""
from typing import Any

from backend.src.services.legal_extractive_answer_service import (
    LegalExtractiveAnswerService,
    _WEAK_LLM_MARKERS,
)


def should_use_extractive_answer(
    answer_text: str,
    chunks: list[dict[str, Any]],
    audience: str,
    question: str = "",
) -> bool:
    """Prefer structured extractive answers when chunks support the product promise."""
    service = LegalExtractiveAnswerService()
    excerpt_count = service.count_usable_excerpts(chunks, question)
    if excerpt_count < 1:
        return False
    if not answer_text or not answer_text.strip():
        return True
    lowered = answer_text.lower()
    if any(marker in lowered for marker in _WEAK_LLM_MARKERS):
        return True
    if "## kort antwoord" not in lowered:
        return True
    if audience == "professional" and not _mentions_articles(lowered):
        return True
    if len(answer_text.strip()) < 120 and excerpt_count >= 2:
        return True
    return False


def _mentions_articles(lowered_answer: str) -> bool:
    return "art." in lowered_answer or "artikel" in lowered_answer or "celex" in lowered_answer

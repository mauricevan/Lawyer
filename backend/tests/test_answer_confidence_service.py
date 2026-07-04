"""Tests for answer confidence scoring."""
from backend.src.services.answer_confidence_service import (
    LOW_CONFIDENCE_THRESHOLD,
    AnswerConfidenceService,
)


def test_high_score_with_strong_chunks() -> None:
    service = AnswerConfidenceService()
    chunks = [{"score": 0.72}, {"score": 0.41}]
    score = service.assess(chunks, "local", citation_count=2)
    assert score >= LOW_CONFIDENCE_THRESHOLD


def test_low_score_without_chunks() -> None:
    service = AnswerConfidenceService()
    assert service.assess([], "local", citation_count=0) == 0.0


def test_live_fallback_lowers_score() -> None:
    service = AnswerConfidenceService()
    chunks = [{"score": 0.4}]
    local = service.assess(chunks, "local", citation_count=1)
    live = service.assess(chunks, "live_fallback", citation_count=1)
    assert live < local


def test_assess_retrieval_ignores_citation_penalty() -> None:
    service = AnswerConfidenceService()
    chunks = [{"score": 0.42}]
    retrieval = service.assess_retrieval(chunks, "local")
    post_llm = service.assess(chunks, "local", citation_count=0)
    assert retrieval > post_llm
    assert retrieval >= 0.35

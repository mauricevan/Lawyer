"""Tests for verification questions on low confidence."""
from backend.src.services.verification_question_service import VerificationQuestionService
from shared.schemas.coverage_guidance import AdequacyResult, CoverageGuidance
from shared.schemas.query import QueryRequest


def test_no_questions_when_confidence_high() -> None:
    service = VerificationQuestionService()
    request = QueryRequest(question="Wat is DORA?", audience="layperson")
    assert service.build(request, confidence=0.8, retrieval_route="local") == []


def test_layperson_questions_when_low_confidence() -> None:
    service = VerificationQuestionService()
    request = QueryRequest(question="Wat is DORA?", audience="layperson")
    questions = service.build(request, confidence=0.1, retrieval_route="live_fallback")
    assert len(questions) >= 2
    assert any("EUR-Lex" in q for q in questions)


def test_coverage_gap_questions_for_workplace_monitoring() -> None:
    service = VerificationQuestionService()
    request = QueryRequest(
        question="Werkgever scant e-mails",
        audience="layperson",
        query_mode="compliance",
    )
    adequacy = AdequacyResult(
        is_adequate=False,
        reason="irrelevant_retrieval",
        coverage_status="irrelevant",
    )
    guidance = CoverageGuidance(topic_id="workplace_monitoring", sensitivity="high")
    questions = service.build(request, 0.2, "local", adequacy, guidance)
    assert any("ondernemingsraad" in q.lower() for q in questions)

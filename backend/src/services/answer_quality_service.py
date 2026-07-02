"""Packages confidence, verification questions, and reliability metrics."""
from shared.schemas.query import QueryRequest

from backend.src.services.answer_confidence_service import AnswerConfidenceService
from backend.src.services.citation_reliability_service import citation_reliability_service
from backend.src.services.verification_question_service import VerificationQuestionService


class AnswerQualityService:
    """Combines H2 quality signals for each answered query."""

    def __init__(self) -> None:
        self._confidence = AnswerConfidenceService()
        self._verification = VerificationQuestionService()

    def package(
        self,
        request: QueryRequest,
        chunks: list[dict],
        retrieval_route: str | None,
        citation_count: int,
    ) -> dict[str, object]:
        score = self._confidence.assess(chunks, retrieval_route, citation_count)
        questions = self._verification.build(request, score, retrieval_route)
        citation_reliability_service.record(citation_count, score, retrieval_route)
        return {
            "confidence_score": score,
            "verification_questions": questions,
        }


answer_quality_service = AnswerQualityService()

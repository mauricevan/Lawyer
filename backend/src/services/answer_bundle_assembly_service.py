"""Assemble finalized answer bundles with policy and quality metadata."""
from backend.src.services.answer_confidence_service import AnswerConfidenceService
from backend.src.services.answer_policy_service import AnswerPolicyService
from backend.src.services.answer_quality_service import answer_quality_service
from backend.src.services.insufficient_coverage_answer_service import InsufficientCoverageAnswerService
from shared.schemas.citation import Citation
from shared.schemas.coverage_guidance import AdequacyResult, CoverageGuidance
from shared.schemas.query import QueryRequest
from backend.src.services.question_intent_service import QuestionIntentAnalysis


class AnswerBundleAssemblyService:
    """Finalizes answer text, citations, and quality packaging."""

    def __init__(self) -> None:
        self._insufficient_answer = InsufficientCoverageAnswerService()
        self._answer_policy = AnswerPolicyService()
        self._confidence = AnswerConfidenceService()

    def gap_bundle(
        self,
        request: QueryRequest,
        chunks: list[dict],
        route: str | None,
        adequacy: AdequacyResult,
        guidance: CoverageGuidance,
        intent: QuestionIntentAnalysis | None = None,
    ) -> dict:
        answer_text = self._insufficient_answer.build(
            guidance, adequacy.reason or "topic_not_in_corpus", request.audience,
            request.question, intent,
        )
        return self.finalize(request, answer_text, [], [], route, adequacy, guidance)

    def insufficient_bundle(
        self,
        request: QueryRequest,
        route: str | None,
        reason: str,
        intent: QuestionIntentAnalysis,
        guidance: CoverageGuidance | None = None,
    ) -> dict:
        guidance = guidance or self._coverage_placeholder(request)
        adequacy = AdequacyResult(is_adequate=False, reason=reason, coverage_status="insufficient")  # type: ignore[arg-type]
        answer_text = self._insufficient_answer.build(
            guidance, reason, request.audience, request.question, intent,
        )  # type: ignore[arg-type]
        return self.finalize(request, answer_text, [], [], route, adequacy, guidance)

    def compare_gap_bundle(self, request: QueryRequest, route: str | None, guidance: CoverageGuidance) -> dict:
        adequacy = AdequacyResult(
            is_adequate=False, reason="topic_not_in_corpus", coverage_status="insufficient",
        )
        answer_text = (
            "## Kort antwoord\n"
            "Voor een vergelijking heb ik minstens twee verschillende regelingen nodig.\n\n"
            "## Wat u wél kunt doen\n"
            "- Formuleer beide regelingen concreet (bijv. wetnaam of CELEX).\n\n"
            "## Let op\nRaadpleeg een jurist bij twijfel."
        )
        return self.finalize(request, answer_text, [], [], route, adequacy, guidance)

    def finalize(
        self,
        request: QueryRequest,
        answer_text: str,
        citations: list[Citation],
        chunks: list[dict],
        route: str | None,
        adequacy: AdequacyResult,
        guidance: CoverageGuidance | None,
        confidence: float | None = None,
    ) -> dict:
        query_language = request.filters.language if request.filters else request.language
        answer_text, citations, disclaimer = self._answer_policy.finalize_answer(
            answer_text, citations, chunks if adequacy.is_adequate else [],
            request.audience, query_language or "nl",
        )
        quality = answer_quality_service.package(
            request, chunks, route, len(citations), adequacy, guidance,
        )
        if adequacy.is_adequate and citations:
            quality["confidence_score"] = confidence or self._confidence.assess(
                chunks, route, len(citations),
            )
        return {
            "answer_text": answer_text,
            "citations": citations,
            "disclaimer": disclaimer,
            "quality": quality,
            "coverage_guidance": guidance,
            "coverage_status": adequacy.coverage_status,
            "retrieval_route": route,
        }

    def _coverage_placeholder(self, request: QueryRequest) -> CoverageGuidance:
        from backend.src.services.coverage_guidance_service import CoverageGuidanceService

        return CoverageGuidanceService().resolve(request.question)

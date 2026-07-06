"""V10.3 ILCL gate — pre-retrieval clarification before legal classification."""
from typing import Any

from backend.src.config import settings
from backend.src.services.layperson_conversation_service import LaypersonConversationService
from backend.src.utils.effective_question_resolver import resolve_effective_question
from backend.src.services.legal_clarification_orchestrator import LegalClarificationOrchestrator
from backend.src.utils.clarification_formatter import (
    clarification_prompt_from_result,
    verification_questions_from_result,
)
from shared.legal.disclaimers import get_disclaimer
from shared.schemas.legal_clarification import LegalClarificationResult
from shared.schemas.query import QueryRequest


class LegalClarificationGateService:
    """Stop or enrich questions before EUR-Lex retrieval."""

    def __init__(self) -> None:
        self._orchestrator = LegalClarificationOrchestrator()
        self._conversation = LaypersonConversationService()

    def gate(
        self,
        request: QueryRequest,
        history: list[dict] | None = None,
    ) -> tuple[QueryRequest, LegalClarificationResult | None, dict[str, Any] | None]:
        """Return enriched request, ILCL metadata, or early clarify bundle."""
        effective = resolve_effective_question(request.question, history)
        result = self._orchestrator.clarify(effective, history, request.audience)
        return self._finalize_gate(request, result, effective)

    async def gate_async(
        self,
        request: QueryRequest,
        history: list[dict] | None = None,
    ) -> tuple[QueryRequest, LegalClarificationResult | None, dict[str, Any] | None]:
        """Async gate with optional conversational LLM enrichment for laypersons."""
        effective = resolve_effective_question(request.question, history)
        result = self._orchestrator.clarify(effective, history, request.audience)
        if self._should_enrich_with_llm(request, result):
            result = await self._conversation.enrich_clarification(result, effective, history)
        return self._finalize_gate(request, result, effective)

    def _should_enrich_with_llm(
        self,
        request: QueryRequest,
        result: LegalClarificationResult,
    ) -> bool:
        return (
            settings.layperson_conversation_llm_enabled
            and request.audience == "layperson"
            and not result.should_proceed
            and result.mode == "questions"
        )

    def _finalize_gate(
        self,
        request: QueryRequest,
        result: LegalClarificationResult,
        effective_question: str,
    ) -> tuple[QueryRequest, LegalClarificationResult | None, dict[str, Any] | None]:
        if result.should_proceed:
            effective = result.enriched_question or effective_question
            enriched_request = request.model_copy(update={"question": effective})
            return enriched_request, result if result.mode != "skip" else None, None
        bundle = self._clarify_bundle(request, result)
        return request, result, bundle

    def _clarify_bundle(self, request: QueryRequest, result: LegalClarificationResult) -> dict[str, Any]:
        questions = verification_questions_from_result(result, request.audience)
        prompt = clarification_prompt_from_result(result)
        status = "clarify_only" if result.state != "unanswerable" else "irrelevant"
        quality: dict[str, Any] = {
            "confidence_score": 0.0,
            "verification_questions": questions,
        }
        if prompt:
            quality["clarification_prompt"] = prompt
        return {
            "answer_text": result.formatted_section,
            "citations": [],
            "disclaimer": get_disclaimer(request.audience, request.language),  # type: ignore[arg-type]
            "quality": quality,
            "coverage_guidance": None,
            "coverage_status": status,
        }

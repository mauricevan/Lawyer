"""Explanation engine orchestrator: compose → publish → render."""
from typing import Any

from backend.src.services.explanation_composer_service import ExplanationComposerService
from backend.src.services.explanation_publish_guard_service import ExplanationPublishGuardService
from backend.src.services.explanation_renderer_service import ExplanationRendererService
from backend.src.services.internal_analysis_orchestrator import InternalAnalysisOrchestrator
from shared.schemas.evidence_validation import EvidenceValidationResult
from shared.schemas.legal_conflict import LegalCaseAnalysis, ReconciliationResult
from shared.schemas.legal_explanation import ExplanationEngineResult, GapResponse, PublishedExplanation
from shared.schemas.legal_interpretation import AgentFetchResult, LegalInterpretationPlan
from shared.schemas.query import QueryRequest


class ExplanationEngineService:
    """Retrieve→Compose→Verify(implicit)→Publish→Render; telemetry spawned after."""

    def __init__(self) -> None:
        self._composer = ExplanationComposerService()
        self._guard = ExplanationPublishGuardService()
        self._renderer = ExplanationRendererService()
        self._telemetry = InternalAnalysisOrchestrator()

    async def run(
        self,
        request: QueryRequest,
        fetch: AgentFetchResult,
        plan: LegalInterpretationPlan,
        history: list[dict] | None,
        evidence: EvidenceValidationResult,
        reconciliation: ReconciliationResult,
        analysis: LegalCaseAnalysis,
    ) -> tuple[ExplanationEngineResult, PublishedExplanation | None]:
        draft = await self._composer.compose(
            request, fetch, plan, history, evidence, reconciliation, analysis,
        )
        outcome = self._guard.publish(draft)
        result = self._outcome_to_result(outcome)
        published = outcome if isinstance(outcome, PublishedExplanation) else None
        if published:
            self._telemetry.spawn(published, analysis)
        return result, published

    async def run_no_domain_gap(self, request: QueryRequest) -> ExplanationEngineResult:
        draft = await self._composer.compose_no_domain_gap(request)
        outcome = self._guard.publish(draft)
        return self._outcome_to_result(outcome)

    async def run_from_draft_bundle(
        self,
        request: QueryRequest,
        fetch: AgentFetchResult,
        bundle: dict[str, Any],
    ) -> ExplanationEngineResult:
        """ILCL / combination paths that already have a bundle."""
        draft = self._composer.bundle_to_draft(bundle, fetch.chunks)
        outcome = self._guard.publish(draft)
        result = self._outcome_to_result(outcome)
        if isinstance(outcome, PublishedExplanation):
            self._telemetry.spawn(outcome, None)
        return result

    def result_to_bundle(self, result: ExplanationEngineResult) -> dict[str, Any]:
        """Map engine result to legacy bundle shape for API layer."""
        return {
            "answer_text": result.answer_markdown,
            "citations": list(result.citations),
            "disclaimer": result.disclaimer,
            "quality": result.quality,
            "coverage_guidance": result.coverage_guidance,
            "coverage_status": result.coverage_status,
            "retrieval_route": "agent_flow",
        }

    def _outcome_to_result(
        self,
        outcome: PublishedExplanation | GapResponse,
    ) -> ExplanationEngineResult:
        if isinstance(outcome, PublishedExplanation):
            return self._renderer.to_engine_result(outcome, None)
        return self._renderer.to_engine_result(None, outcome)

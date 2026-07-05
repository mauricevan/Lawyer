"""Sole writer of LegalExplanationDraft — wraps retrieval answer path once."""
from typing import Any

from backend.src.services.agent_answer_service import AgentAnswerService
from backend.src.utils.explanation_draft_json_parser import parse_sections_json
from backend.src.utils.explanation_section_mapper import markdown_to_sections, retrieval_context_id
from shared.schemas.evidence_validation import EvidenceValidationResult
from shared.schemas.legal_conflict import LegalCaseAnalysis, ReconciliationResult
from shared.schemas.legal_explanation import LegalExplanationDraft
from shared.schemas.legal_interpretation import AgentFetchResult, LegalInterpretationPlan
from shared.schemas.query import QueryRequest


class ExplanationComposerService:
    """Only service allowed to create explanation content."""

    def __init__(self) -> None:
        self._answer = AgentAnswerService()

    async def compose(
        self,
        request: QueryRequest,
        fetch: AgentFetchResult,
        plan: LegalInterpretationPlan,
        history: list[dict] | None,
        evidence: EvidenceValidationResult | None,
        reconciliation: ReconciliationResult | None,
        analysis: LegalCaseAnalysis | None,
    ) -> LegalExplanationDraft:
        """Build draft from agent answer path — single write, then freeze."""
        bundle = await self._build_bundle(
            request, fetch, plan, history, evidence, reconciliation, analysis,
        )
        return self.bundle_to_draft(bundle, fetch.chunks)

    async def compose_no_domain_gap(self, request: QueryRequest) -> LegalExplanationDraft:
        bundle = await self._answer.build_no_domain_gap(request)
        return self.bundle_to_draft(bundle, [])

    async def _build_bundle(
        self,
        request: QueryRequest,
        fetch: AgentFetchResult,
        plan: LegalInterpretationPlan,
        history: list[dict] | None,
        evidence: EvidenceValidationResult | None,
        reconciliation: ReconciliationResult | None,
        analysis: LegalCaseAnalysis | None,
    ) -> dict[str, Any]:
        return await self._answer.build(
            request, fetch, plan, history, evidence, reconciliation, analysis,
        )

    def bundle_to_draft(self, bundle: dict[str, Any], chunks: list[dict]) -> LegalExplanationDraft:
        """Convert legacy bundle to frozen draft (for ILCL/combination paths)."""
        disclaimer = str(bundle.get("disclaimer", ""))
        answer_text = str(bundle.get("answer_text", ""))
        parsed = parse_sections_json(answer_text)
        sections = parsed or markdown_to_sections(answer_text, disclaimer)
        citations = tuple(bundle.get("citations") or [])
        guidance = bundle.get("coverage_guidance")
        return LegalExplanationDraft(
            sections=sections,
            citations=citations,
            coverage_status=bundle.get("coverage_status", "insufficient"),
            retrieval_context_id=retrieval_context_id(chunks),
            quality=dict(bundle.get("quality") or {}),
            coverage_guidance=guidance.model_dump(mode="json") if guidance else None,
        )

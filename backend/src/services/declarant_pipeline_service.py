"""Declarant pipeline — think → clarify → fetch → verify → answer."""
from collections.abc import AsyncIterator
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from backend.src.services.answer_bundle_assembly_service import AnswerBundleAssemblyService
from backend.src.services.citation_builder_service import CitationBuilderService
from backend.src.services.citation_verifier_service import CitationVerifierService
from backend.src.services.coverage_guidance_service import CoverageGuidanceService
from backend.src.services.declarant_fetch_service import DeclarantFetchService
from backend.src.services.declarant_plan_builder_service import DeclarantPlanBuilderService
from backend.src.services.declarant_response_builder import DeclarantResponseBuilder
from backend.src.services.declarant_think_service import DeclarantThinkService
from backend.src.services.evidence_validation_service import EvidenceValidationService
from backend.src.services.explanation_engine_service import ExplanationEngineService
from backend.src.services.layperson_clear_answer_composer import LaypersonClearAnswerComposer
from backend.src.services.legal_case_analysis_service import LegalCaseAnalysisService
from backend.src.utils.clarification_history_merge import clarification_turn_count
from backend.src.utils.national_law_boundary import render_national_law_boundary
from shared.schemas.coverage_guidance import AdequacyResult
from shared.schemas.declarant_dossier import DeclarantPhase
from shared.schemas.legal_hypothesis import LegalHypothesis
from shared.schemas.legal_interpretation import AgentFetchResult, LegalInterpretationPlan
from shared.schemas.query import QueryRequest

_MAX_CLARIFICATION_ROUNDS = 2


class DeclarantPipelineService:
    """Single layperson route: reason first, then EUR-Lex, then grounded answer."""

    def __init__(self) -> None:
        self._think = DeclarantThinkService()
        self._plan_builder = DeclarantPlanBuilderService()
        self._fetch = DeclarantFetchService()
        self._evidence = EvidenceValidationService()
        self._composer = LaypersonClearAnswerComposer()
        self._verifier = CitationVerifierService()
        self._citations = CitationBuilderService()
        self._assembly = AnswerBundleAssemblyService()
        self._coverage = CoverageGuidanceService()
        self._responses = DeclarantResponseBuilder()
        self._engine = ExplanationEngineService()
        self._case = LegalCaseAnalysisService()

    async def run(
        self,
        request: QueryRequest,
        history: list[dict] | None,
        session: AsyncSession | None,
    ) -> tuple[LegalInterpretationPlan, AgentFetchResult, dict[str, Any], LegalHypothesis]:
        bundle, plan, fetch, hypothesis = await self._execute(request, history, session)
        result = await self._engine.run_from_draft_bundle(request, fetch, bundle)
        final_bundle = self._engine.result_to_bundle(result)
        return plan, fetch, final_bundle, hypothesis

    async def run_with_events(
        self,
        request: QueryRequest,
        history: list[dict] | None,
        session: AsyncSession | None,
    ) -> AsyncIterator[dict[str, Any]]:
        yield {"step": "clarifying", "message": "Ik bekijk wat u bedoelt…"}
        bundle, plan, fetch, hypothesis = await self._execute(request, history, session)
        yield {"step": "clarified", "message": _clarified_message(bundle)}
        if fetch.chunks:
            yield {
                "step": "found",
                "message": "Relevante EU-regels gevonden",
                "detail": {"count": len(fetch.chunks), "retrieval_chunks": fetch.chunks},
            }
        yield {"step": "generating", "message": "Ik stel een antwoord voor u samen…"}
        result = await self._engine.run_from_draft_bundle(request, fetch, bundle)
        final = self._engine.result_to_bundle(result)
        yield _complete_event(request, final, hypothesis, plan)

    async def _execute(
        self,
        request: QueryRequest,
        history: list[dict] | None,
        session: AsyncSession | None,
    ) -> tuple[dict[str, Any], LegalInterpretationPlan, AgentFetchResult, LegalHypothesis]:
        think = await self._think.think(request, history)
        analysis = think.analysis
        hypothesis = self._case.to_hypothesis(analysis) if analysis else _fallback_hypothesis(request)
        empty_fetch = AgentFetchResult(chunks=[], fetch_ok=False, fetch_attempted=False)
        plan = LegalInterpretationPlan()

        if think.phase == DeclarantPhase.GAP:
            bundle = self._responses.gap_bundle(request, think.gap_reason or "Geen EU-bron gevonden.")
            return bundle, plan, empty_fetch, hypothesis

        if think.phase == DeclarantPhase.CLARIFY and think.ilcl_result:
            bundle = self._responses.clarify_bundle(request, think.ilcl_result)
            return bundle, plan, empty_fetch, hypothesis

        enriched = request.model_copy(update={"question": think.effective_question})
        plan = self._plan_builder.build(think)
        fetch = await self._fetch.fetch(plan, enriched, session)

        if self._fetch.needs_more_context(fetch, plan):
            if clarification_turn_count(history) < _MAX_CLARIFICATION_ROUNDS:
                bundle = self._responses.fetch_clarify_bundle(request, think.effective_question)
                return bundle, plan, fetch, hypothesis
            bundle = self._responses.gap_bundle(
                request,
                "EUR-Lex leverde geen bruikbare wettekst voor deze formulering.",
            )
            return bundle, plan, fetch, hypothesis

        evidence = self._evidence.validate(
            think.effective_question, fetch.chunks, plan, hypothesis, analysis,
        )
        if not evidence.is_valid:
            if clarification_turn_count(history) < _MAX_CLARIFICATION_ROUNDS:
                bundle = self._responses.fetch_clarify_bundle(request, think.effective_question)
                return bundle, plan, fetch, hypothesis
            bundle = self._responses.gap_bundle(
                request,
                "De gevonden EU-tekst past niet genoeg bij uw vraag.",
            )
            return bundle, plan, fetch, hypothesis

        from backend.src.utils.declarant_answer_formatter import build_declarant_verified_answer

        answer_text = build_declarant_verified_answer(think.effective_question, fetch.chunks)
        if not answer_text:
            answer_text = self._composer.compose_without_llm(think.effective_question, fetch.chunks)
        if not answer_text:
            bundle = self._responses.gap_bundle(request, "Kon geen leesbaar antwoord samenstellen uit EUR-Lex.")
            return bundle, plan, fetch, hypothesis

        if analysis:
            boundary = render_national_law_boundary(analysis)
            if boundary and "## EU-recht en nationaal recht" not in answer_text:
                answer_text = f"{answer_text.rstrip()}\n\n{boundary}"

        supported, verified_text, _issues = await self._verifier.verify(
            answer_text, fetch.chunks, plan, extractive_only=True,
        )
        if not supported:
            bundle = self._responses.gap_bundle(request, "Het antwoord kon niet worden geverifieerd tegen EUR-Lex.")
            return bundle, plan, fetch, hypothesis

        citations = self._citations.from_chunks_for_answer(verified_text, fetch.chunks)
        if not citations:
            citations = self._citations.from_plan_instruments(plan, verified_text)
        guidance = self._coverage.resolve(request.question)
        adequacy = AdequacyResult(is_adequate=True, coverage_status="adequate")
        bundle = self._assembly.finalize(
            enriched, verified_text.strip(), citations, fetch.chunks,
            "declarant_flow", adequacy, guidance,
        )
        return bundle, plan, fetch, hypothesis


def _fallback_hypothesis(request: QueryRequest) -> LegalHypothesis:
    return LegalHypothesis(legal_problem=request.question, source="rule")


def _clarified_message(bundle: dict[str, Any]) -> str:
    if bundle.get("coverage_status") == "clarify_only":
        return "Nog details nodig — kies hieronder."
    return "Ik zoek de EU-regels op."


def _complete_event(
    request: QueryRequest,
    bundle: dict[str, Any],
    hypothesis: LegalHypothesis,
    plan: LegalInterpretationPlan,
) -> dict[str, Any]:
    guidance = bundle.get("coverage_guidance")
    citations = bundle.get("citations", [])
    serialized_citations = [
        c.model_dump(mode="json") if hasattr(c, "model_dump") else c
        for c in citations
    ]
    detail: dict[str, Any] = {
        "answer": bundle["answer_text"],
        "conversation_id": request.conversation_id,
        "citations": serialized_citations,
        "disclaimer": bundle.get("disclaimer", ""),
        "retrieval_route": "declarant_flow",
        "confidence_score": bundle.get("quality", {}).get("confidence_score"),
        "verification_questions": bundle.get("quality", {}).get("verification_questions", []),
        "clarification_prompt": bundle.get("quality", {}).get("clarification_prompt"),
        "coverage_guidance": (
            guidance.model_dump(mode="json")
            if hasattr(guidance, "model_dump")
            else guidance if isinstance(guidance, dict) else None
        ),
        "coverage_status": bundle.get("coverage_status"),
        "interpretation_plan": plan.model_dump(mode="json"),
    }
    return {"step": "complete", "message": "Klaar", "detail": detail}

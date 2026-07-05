"""V4 pipeline: retrieve → compose → publish → render (immutable explanation engine)."""
from collections.abc import AsyncIterator
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from backend.src.services.article_fetch_orchestrator_service import ArticleFetchOrchestratorService
from backend.src.services.conflict_aware_celex_resolver_service import ConflictAwareCelexResolverService
from backend.src.services.combination_path_detector_service import detect_combination_plan
from backend.src.services.combination_path_handler_service import CombinationPathHandlerService
from backend.src.services.evidence_gate_service import EvidenceGateService
from backend.src.services.explanation_engine_service import ExplanationEngineService
from backend.src.services.instrument_resolver_service import InstrumentResolverService
from backend.src.services.legal_case_analysis_service import LegalCaseAnalysisService
from backend.src.services.legal_clarification_gate_service import LegalClarificationGateService
from backend.src.services.legal_reconciliation_service import LegalReconciliationService
from backend.src.services.llm_legal_planner_service import LlmLegalPlannerService
from backend.src.utils.explanation_explainability_builder import build_retrieval_explainability
from backend.src.utils.hypothesis_plan_merge import merge_case_analysis_into_plan
from backend.src.utils.hypothesis_retrieval_query import build_analysis_retrieval_query
from shared.schemas.celex_resolution import CelexResolutionResult
from shared.schemas.evidence_validation import EvidenceValidationResult
from shared.schemas.legal_conflict import LegalCaseAnalysis, ReconciliationResult
from shared.schemas.legal_hypothesis import LegalHypothesis
from shared.schemas.legal_interpretation import AgentFetchResult, LegalInterpretationPlan
from shared.schemas.query import QueryRequest
from shared.schemas.retrieval_explainability import RetrievalExplainability


class AgentV4PipelineService:
    """Retrieve EU sources → explanation engine → respond. No post-publish mutation."""

    def __init__(self) -> None:
        self._case_analysis = LegalCaseAnalysisService()
        self._planner = LlmLegalPlannerService()
        self._resolver = InstrumentResolverService()
        self._celex_resolver = ConflictAwareCelexResolverService()
        self._fetcher = ArticleFetchOrchestratorService()
        self._evidence_gate = EvidenceGateService()
        self._reconciliation = LegalReconciliationService()
        self._engine = ExplanationEngineService()
        self._ilcl_gate = LegalClarificationGateService()

    async def run(
        self,
        request: QueryRequest,
        history: list[dict] | None,
        session: AsyncSession | None,
    ) -> tuple[
        LegalInterpretationPlan,
        AgentFetchResult,
        dict[str, Any],
        LegalHypothesis,
        EvidenceValidationResult,
        ReconciliationResult,
        LegalCaseAnalysis,
    ]:
        request, _ilcl, ilcl_bundle = await self._ilcl_gate.gate_async(request, history)
        if ilcl_bundle is not None:
            return await self._ilcl_early_return(request, ilcl_bundle)
        combo = detect_combination_plan(request.question)
        if combo is not None:
            return await CombinationPathHandlerService(self).run(request, history, session, combo)
        ctx = await self._retrieve(request, history, session)
        return self._tuple_from_ctx(ctx)

    async def run_with_events(
        self,
        request: QueryRequest,
        history: list[dict] | None,
        session: AsyncSession | None,
    ) -> AsyncIterator[dict[str, Any]]:
        is_layperson = request.audience == "layperson"
        yield _step("clarifying", _msg(is_layperson, "Ik bekijk wat u bedoelt…", "ILCL…"))
        request, ilcl_result, ilcl_bundle = await self._ilcl_gate.gate_async(request, history)
        yield _step("clarified", _clarified_msg(is_layperson, ilcl_bundle is not None))
        if ilcl_bundle is not None:
            bundle = await self._engine.run_from_draft_bundle(
                request, AgentFetchResult(chunks=[], fetch_ok=False), ilcl_bundle,
            )
            yield _complete(request, self._engine.result_to_bundle(bundle), _ilcl_hypothesis(request), False, "contradicted", _ilcl_analysis(request))
            return
        if detect_combination_plan(request.question) is not None:
            async for event in self._stream_combination(request, history, session):
                yield event
            return
        async for event in self._stream_explanation(request, history, session, ilcl_result, is_layperson):
            yield event

    async def _retrieve(
        self,
        request: QueryRequest,
        history: list[dict] | None,
        session: AsyncSession | None,
    ) -> dict[str, Any]:
        analysis = await self._case_analysis.analyze(request.question, history)
        hypothesis = self._enrich_hypothesis(self._case_analysis.to_hypothesis(analysis))
        empty_fetch = AgentFetchResult(chunks=[], fetch_ok=False, fetch_attempted=False)
        if analysis.legal_domain == "unknown":
            result = await self._engine.run_no_domain_gap(request)
            return self._ctx_from_result(
                LegalInterpretationPlan(), empty_fetch, result, hypothesis,
                EvidenceValidationResult(is_valid=False, reasons=["no_chunks"]),
                ReconciliationResult(conclusion="contradicted", rationale="Geen rechtsgebied."),
                analysis, None,
            )
        plan = await self._planner.interpret(request.question, history)
        resolved = merge_case_analysis_into_plan(plan, analysis)
        retrieval_query = build_analysis_retrieval_query(analysis)
        resolved, celex_resolution = await self._resolve_with_conflict_celex(
            analysis, resolved, request, retrieval_query,
        )
        fetch = await self._fetcher.fetch(resolved, request, session)
        fetch, evidence = await self._evidence_gate.gate(
            request, resolved, fetch, session, hypothesis, analysis, celex_resolution, history,
        )
        reconciliation = self._reconciliation.reconcile(analysis, fetch.chunks, evidence)
        hypothesis = hypothesis.model_copy(update={"reconciliation_conclusion": reconciliation.conclusion})
        engine_result, _published = await self._engine.run(
            request, fetch, resolved, history, evidence, reconciliation, analysis,
        )
        bundle = self._engine.result_to_bundle(engine_result)
        if evidence.g3_trace:
            bundle = {**bundle, "g3_trace": evidence.g3_trace}
        return self._ctx_from_bundle(
            resolved, fetch, bundle, hypothesis, evidence, reconciliation, analysis, celex_resolution,
        )

    async def _stream_explanation(
        self,
        request: QueryRequest,
        history: list[dict] | None,
        session: AsyncSession | None,
        ilcl_result: Any,
        is_layperson: bool,
    ) -> AsyncIterator[dict[str, Any]]:
        if not is_layperson:
            yield _step("hypothesis", "Legal case analysis…")
        yield _step("fetching", _msg(is_layperson, "Ik haal EU-bronnen op…", "Fetching…"))
        ctx = await self._retrieve(request, history, session)
        yield _step("validating", _msg(is_layperson, "Ik controleer de bronnen…", "Validating…"), {"chunk_count": len(ctx["fetch"].chunks)})
        yield _step("generating", _msg(is_layperson, "Ik stel uw antwoord samen…", "Composing…"))
        explain = build_retrieval_explainability(
            ctx["resolved"], ctx["fetch"], ctx["hypothesis"], ctx["evidence"],
            ctx["reconciliation"], ctx["analysis"], ctx["celex_resolution"], ilcl_result,
        )
        yield _complete(
            request, ctx["bundle"], ctx["hypothesis"], ctx["evidence"].is_valid,
            ctx["reconciliation"].conclusion, ctx["analysis"], ctx["resolved"], explain,
        )

    async def _stream_combination(
        self,
        request: QueryRequest,
        history: list[dict] | None,
        session: AsyncSession | None,
    ) -> AsyncIterator[dict[str, Any]]:
        combo = detect_combination_plan(request.question)
        yield _step("generating", "Combination path.")
        resolved, fetch, bundle, hypothesis, evidence, reconciliation, analysis = (
            await CombinationPathHandlerService(self).run(request, history, session, combo)
        )
        yield _complete(
            request, bundle, hypothesis, evidence.is_valid if evidence else False,
            reconciliation.conclusion, analysis, resolved,
        )

    async def _ilcl_early_return(
        self,
        request: QueryRequest,
        ilcl_bundle: dict[str, Any],
    ) -> tuple[LegalInterpretationPlan, AgentFetchResult, dict[str, Any], LegalHypothesis, EvidenceValidationResult, ReconciliationResult, LegalCaseAnalysis]:
        empty = AgentFetchResult(chunks=[], fetch_ok=False, fetch_attempted=False)
        result = await self._engine.run_from_draft_bundle(request, empty, ilcl_bundle)
        bundle = self._engine.result_to_bundle(result)
        return (
            LegalInterpretationPlan(), empty, bundle, _ilcl_hypothesis(request),
            EvidenceValidationResult(is_valid=False, reasons=["ilcl_clarification"]),
            ReconciliationResult(conclusion="contradicted", rationale="ILCL-verduidelijking vereist."),
            _ilcl_analysis(request),
        )

    def _tuple_from_ctx(self, ctx: dict[str, Any]) -> tuple[Any, ...]:
        return (
            ctx["resolved"], ctx["fetch"], ctx["bundle"], ctx["hypothesis"],
            ctx["evidence"], ctx["reconciliation"], ctx["analysis"],
        )

    def _ctx_from_result(
        self,
        resolved: LegalInterpretationPlan,
        fetch: AgentFetchResult,
        result: Any,
        hypothesis: LegalHypothesis,
        evidence: EvidenceValidationResult,
        reconciliation: ReconciliationResult,
        analysis: LegalCaseAnalysis,
        celex_resolution: CelexResolutionResult | None,
    ) -> dict[str, Any]:
        bundle = self._engine.result_to_bundle(result)
        return self._ctx_from_bundle(
            resolved, fetch, bundle, hypothesis, evidence, reconciliation, analysis, celex_resolution,
        )

    def _ctx_from_bundle(
        self,
        resolved: LegalInterpretationPlan,
        fetch: AgentFetchResult,
        bundle: dict[str, Any],
        hypothesis: LegalHypothesis,
        evidence: EvidenceValidationResult,
        reconciliation: ReconciliationResult,
        analysis: LegalCaseAnalysis,
        celex_resolution: CelexResolutionResult | None,
    ) -> dict[str, Any]:
        return {
            "resolved": resolved,
            "fetch": fetch,
            "bundle": bundle,
            "hypothesis": hypothesis,
            "evidence": evidence,
            "reconciliation": reconciliation,
            "analysis": analysis,
            "celex_resolution": celex_resolution,
        }

    def _enrich_hypothesis(self, hypothesis: LegalHypothesis) -> LegalHypothesis:
        if not hypothesis.case_summary:
            return hypothesis.model_copy(update={"case_summary": hypothesis.legal_problem})
        return hypothesis

    async def _resolve_with_conflict_celex(
        self,
        analysis: LegalCaseAnalysis,
        plan: LegalInterpretationPlan,
        request: QueryRequest,
        retrieval_query: str,
    ) -> tuple[LegalInterpretationPlan, CelexResolutionResult]:
        resolved = await self._resolver.resolve(plan, request.question, request.language, retrieval_query)
        discovery = [item.celex for item in resolved.instruments if item.celex]
        resolution = self._celex_resolver.resolve(analysis, resolved, discovery)
        return self._celex_resolver.apply_to_plan(resolved, resolution), resolution


def _msg(layperson: bool, nl: str, pro: str) -> str:
    return nl if layperson else pro


def _clarified_msg(layperson: bool, needs_clarify: bool) -> str:
    if not layperson:
        return "ILCL complete."
    return "Nog details nodig — kies hieronder." if needs_clarify else "Ik zoek de EU-regels op."


def _ilcl_hypothesis(request: QueryRequest) -> LegalHypothesis:
    return LegalHypothesis(legal_problem=request.question, source="rule")


def _ilcl_analysis(request: QueryRequest) -> LegalCaseAnalysis:
    return LegalCaseAnalysis(
        case_summary=request.question,
        context="ILCL clarification",
        primary_legal_conflict="platform_governance_issue",
        legal_domain="unknown",
        legal_question_type="obligations",
    )


def _step(step: str, message: str, detail: dict | None = None) -> dict[str, Any]:
    payload: dict[str, Any] = {"step": step, "message": message}
    if detail:
        payload["detail"] = detail
    return payload


def _complete(
    request: QueryRequest,
    bundle: dict[str, Any],
    hypothesis: LegalHypothesis,
    evidence_valid: bool,
    reconciliation: str,
    analysis: LegalCaseAnalysis,
    resolved: LegalInterpretationPlan | None = None,
    explain: RetrievalExplainability | None = None,
) -> dict[str, Any]:
    guidance = bundle.get("coverage_guidance")
    detail: dict[str, Any] = {
        "answer": bundle["answer_text"],
        "conversation_id": request.conversation_id,
        "citations": [c.model_dump(mode="json") if hasattr(c, "model_dump") else c for c in bundle["citations"]],
        "disclaimer": bundle["disclaimer"],
        "retrieval_route": "agent_flow",
        "confidence_score": bundle["quality"].get("confidence_score"),
        "verification_questions": bundle["quality"].get("verification_questions", []),
        "clarification_prompt": bundle["quality"].get("clarification_prompt"),
        "coverage_guidance": guidance if isinstance(guidance, dict) else (guidance.model_dump(mode="json") if guidance else None),
        "coverage_status": bundle["coverage_status"],
        "primary_legal_conflict": analysis.primary_legal_conflict,
        "evidence_valid": evidence_valid,
        "reconciliation_conclusion": reconciliation,
    }
    if request.audience == "professional":
        detail["legal_hypothesis"] = hypothesis.model_dump(mode="json")
    if resolved:
        detail["interpretation_plan"] = resolved.model_dump(mode="json")
    if explain:
        detail["retrieval_explainability"] = explain.model_dump(mode="json")
    if bundle.get("g3_trace"):
        detail["g3_trace"] = bundle["g3_trace"]
    return {"step": "complete", "message": "Klaar", "detail": detail}

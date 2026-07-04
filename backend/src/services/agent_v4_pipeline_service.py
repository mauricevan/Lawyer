"""V4 agent pipeline: conflict → domain → retrieval → evidence → reconciliation → answer."""
from collections.abc import AsyncIterator
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from backend.src.services.agent_answer_service import AgentAnswerService
from backend.src.services.article_fetch_orchestrator_service import ArticleFetchOrchestratorService
from backend.src.services.conflict_aware_celex_resolver_service import ConflictAwareCelexResolverService
from backend.src.services.evidence_gate_service import EvidenceGateService
from backend.src.services.instrument_resolver_service import InstrumentResolverService
from backend.src.services.legal_case_analysis_service import LegalCaseAnalysisService
from backend.src.services.legal_reconciliation_service import LegalReconciliationService
from backend.src.services.llm_legal_planner_service import LlmLegalPlannerService
from backend.src.utils.hypothesis_plan_merge import merge_case_analysis_into_plan
from backend.src.utils.hypothesis_retrieval_query import build_analysis_retrieval_query
from shared.schemas.celex_resolution import CelexResolutionResult
from shared.schemas.evidence_validation import EvidenceValidationResult
from shared.schemas.legal_conflict import LegalCaseAnalysis, ReconciliationResult
from shared.schemas.legal_hypothesis import LegalHypothesis
from shared.schemas.legal_interpretation import AgentFetchResult, LegalInterpretationPlan
from shared.schemas.query import QueryRequest
from shared.schemas.retrieval_explainability import RetrievalExplainability, RouterDecision


class AgentV4PipelineService:
    """Orchestrate V4 legal reasoning before and after EUR-Lex retrieval."""

    def __init__(self) -> None:
        self._case_analysis = LegalCaseAnalysisService()
        self._planner = LlmLegalPlannerService()
        self._resolver = InstrumentResolverService()
        self._celex_resolver = ConflictAwareCelexResolverService()
        self._fetcher = ArticleFetchOrchestratorService()
        self._evidence_gate = EvidenceGateService()
        self._reconciliation = LegalReconciliationService()
        self._answer = AgentAnswerService()

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
        """Execute full V4 flow; hard-fail when domain cannot be determined."""
        analysis = await self._case_analysis.analyze(request.question, history)
        hypothesis = self._enrich_hypothesis(self._case_analysis.to_hypothesis(analysis))
        if analysis.legal_domain == "unknown":
            bundle = await self._answer.build_no_domain_gap(request)
            empty_fetch = AgentFetchResult(chunks=[], fetch_ok=False, fetch_attempted=False)
            evidence = EvidenceValidationResult(is_valid=False, reasons=["no_chunks"])
            reconciliation = ReconciliationResult(
                conclusion="contradicted",
                rationale="Geen rechtsgebied bepaald — geen retrieval.",
            )
            return (
                LegalInterpretationPlan(),
                empty_fetch,
                bundle,
                hypothesis,
                evidence,
                reconciliation,
                analysis,
            )
        plan = await self._planner.interpret(request.question, history)
        resolved = merge_case_analysis_into_plan(plan, analysis)
        retrieval_query = build_analysis_retrieval_query(analysis)
        resolved, celex_resolution = await self._resolve_with_conflict_celex(
            analysis, resolved, request, retrieval_query,
        )
        fetch = await self._fetcher.fetch(resolved, request, session)
        fetch, evidence = await self._evidence_gate.gate(
            request, resolved, fetch, session, hypothesis, analysis, celex_resolution,
        )
        reconciliation = self._reconciliation.reconcile(analysis, fetch.chunks, evidence)
        hypothesis = hypothesis.model_copy(update={
            "reconciliation_conclusion": reconciliation.conclusion,
        })
        bundle = await self._answer.build(
            request, fetch, resolved, history, evidence, reconciliation, analysis,
        )
        return resolved, fetch, bundle, hypothesis, evidence, reconciliation, analysis

    async def run_with_events(
        self,
        request: QueryRequest,
        history: list[dict] | None,
        session: AsyncSession | None,
    ) -> AsyncIterator[dict[str, Any]]:
        """Stream V4 pipeline steps for the frontend."""
        is_layperson = request.audience == "layperson"
        yield _step(
            "hypothesis",
            "Ik analyseer eerst de juridische situatie…" if is_layperson else "Legal case analysis…",
        )
        analysis = await self._case_analysis.analyze(request.question, history)
        hypothesis = self._enrich_hypothesis(self._case_analysis.to_hypothesis(analysis))
        yield _step(
            "conflict",
            "Ik bepaal het primaire juridische conflict…" if is_layperson else "Primary legal conflict…",
            {"legal_hypothesis": hypothesis.model_dump(mode="json")},
        )
        yield _step(
            "effect",
            "Ik bepaal het juridische effect van de maatregel…" if is_layperson else "Legal effect…",
            {
                "legal_effect": (
                    analysis.legal_effect.model_dump(mode="json")
                    if analysis.legal_effect
                    else None
                ),
            },
        )
        if analysis.legal_domain == "unknown":
            bundle = await self._answer.build_no_domain_gap(request)
            yield _complete(request, bundle, hypothesis, False, "contradicted", analysis)
            return
        yield _step(
            "planning",
            "Ik koppel het conflict aan EU-kaders…" if is_layperson else "Domain mapping…",
        )
        plan = await self._planner.interpret(request.question, history)
        resolved = merge_case_analysis_into_plan(plan, analysis)
        retrieval_query = build_analysis_retrieval_query(analysis)
        yield _step(
            "resolving",
            "Ik zoek EU-regelgeving op basis van het conflict…" if is_layperson else "Instrument resolver…",
            {"interpretation_plan": resolved.model_dump(mode="json"), "retrieval_query": retrieval_query},
        )
        resolved, celex_resolution = await self._resolve_with_conflict_celex(
            analysis, resolved, request, retrieval_query,
        )
        yield _step(
            "celex",
            "Ik kies de juridisch juiste EU-bronnen…" if is_layperson else "Conflict-aware CELEX…",
            {"celex_resolution": celex_resolution.model_dump(mode="json")},
        )
        yield _step(
            "fetching",
            "Ik haal artikelteksten op van EUR-Lex…" if is_layperson else "Live artikel-fetch…",
            {"resolved_celex": [i.celex for i in resolved.instruments if i.celex]},
        )
        fetch = await self._fetcher.fetch(resolved, request, session)
        yield _step(
            "validating",
            "Ik controleer of de bronnen het conflict ondersteunen…" if is_layperson else "Evidence validation…",
            {"chunk_count": len(fetch.chunks)},
        )
        fetch, evidence = await self._evidence_gate.gate(
            request, resolved, fetch, session, hypothesis, analysis, celex_resolution,
        )
        reconciliation = self._reconciliation.reconcile(analysis, fetch.chunks, evidence)
        hypothesis = hypothesis.model_copy(update={
            "reconciliation_conclusion": reconciliation.conclusion,
        })
        yield _step(
            "reconciling",
            "Ik vergelijk de analyse met de EU-bronnen…" if is_layperson else "Legal reconciliation…",
            {"reconciliation": reconciliation.model_dump(mode="json")},
        )
        bundle = await self._answer.build(
            request, fetch, resolved, history, evidence, reconciliation, analysis,
        )
        explain = _build_explainability(
            resolved, fetch, hypothesis, evidence, reconciliation, analysis, celex_resolution,
        )
        yield _complete(
            request, bundle, hypothesis, evidence.is_valid, reconciliation.conclusion,
            analysis, resolved, explain,
        )

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
        """Run instrument resolver then V5.1 conflict-aware CELEX override."""
        resolved = await self._resolver.resolve(
            plan, request.question, request.language, retrieval_query,
        )
        discovery = [item.celex for item in resolved.instruments if item.celex]
        resolution = self._celex_resolver.resolve(analysis, resolved, discovery)
        return self._celex_resolver.apply_to_plan(resolved, resolution), resolution


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
    detail: dict[str, Any] = {
        "answer": bundle["answer_text"],
        "conversation_id": request.conversation_id,
        "citations": [c.model_dump(mode="json") for c in bundle["citations"]],
        "disclaimer": bundle["disclaimer"],
        "retrieval_route": "agent_flow",
        "confidence_score": bundle["quality"]["confidence_score"],
        "verification_questions": bundle["quality"]["verification_questions"],
        "coverage_guidance": (
            bundle["coverage_guidance"].model_dump(mode="json")
            if bundle["coverage_guidance"]
            else None
        ),
        "coverage_status": bundle["coverage_status"],
        "legal_hypothesis": hypothesis.model_dump(mode="json"),
        "primary_legal_conflict": analysis.primary_legal_conflict,
        "evidence_valid": evidence_valid,
        "reconciliation_conclusion": reconciliation,
    }
    if resolved:
        detail["interpretation_plan"] = resolved.model_dump(mode="json")
    if explain:
        detail["retrieval_explainability"] = explain.model_dump(mode="json")
    return {"step": "complete", "message": "Klaar", "detail": detail}


def _build_explainability(
    plan: LegalInterpretationPlan,
    fetch: AgentFetchResult,
    hypothesis: LegalHypothesis,
    evidence: EvidenceValidationResult,
    reconciliation: ReconciliationResult,
    analysis: LegalCaseAnalysis,
    celex_resolution: CelexResolutionResult | None = None,
) -> RetrievalExplainability:
    payload = plan.model_dump(mode="json")
    payload["legal_hypothesis"] = hypothesis.model_dump(mode="json")
    payload["evidence_valid"] = evidence.is_valid
    payload["evidence_reasons"] = evidence.reasons
    payload["primary_legal_conflict"] = analysis.primary_legal_conflict
    payload["reconciliation_conclusion"] = reconciliation.conclusion
    if celex_resolution:
        payload["celex_resolution"] = celex_resolution.model_dump(mode="json")
    if analysis.legal_effect:
        payload["legal_effect"] = analysis.legal_effect.model_dump(mode="json")
    return RetrievalExplainability(
        route="live_fallback",
        query_language="nl",
        router=RouterDecision(),
        reranker_variant="agent",
        rerank_latency_ms=0.0,
        hybrid_rrf_enabled=False,
        chunk_count=len(fetch.chunks),
        interpretation_plan=payload,
        resolved_celex=[i.celex for i in plan.instruments if i.celex],
        articles_fetched=fetch.articles_fetched,
        fetch_source=fetch.fetch_source,
    )

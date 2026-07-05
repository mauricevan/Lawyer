"""Retrieval explainability for explanation engine — no simulation leakage by default."""
from shared.schemas.celex_resolution import CelexResolutionResult
from shared.schemas.evidence_validation import EvidenceValidationResult
from shared.schemas.legal_clarification import LegalClarificationResult
from shared.schemas.legal_conflict import LegalCaseAnalysis, ReconciliationResult
from shared.schemas.legal_hypothesis import LegalHypothesis
from shared.schemas.legal_interpretation import AgentFetchResult, LegalInterpretationPlan
from shared.schemas.retrieval_explainability import RetrievalExplainability, RouterDecision

_SIMULATION_KEYS = frozenset({
    "legal_judge",
    "case_law_simulation",
    "multi_judge_panel",
    "doctrine_evolution",
    "doctrine_anchoring",
    "doctrine_stability",
})


def build_retrieval_explainability(
    plan: LegalInterpretationPlan,
    fetch: AgentFetchResult,
    hypothesis: LegalHypothesis,
    evidence: EvidenceValidationResult,
    reconciliation: ReconciliationResult,
    analysis: LegalCaseAnalysis,
    celex_resolution: CelexResolutionResult | None = None,
    ilcl_result: LegalClarificationResult | None = None,
    include_simulation_telemetry: bool = False,
) -> RetrievalExplainability:
    """Build routing explainability; simulation keys omitted unless admin telemetry."""
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
    if ilcl_result:
        payload["legal_clarification"] = ilcl_result.model_dump(mode="json")
    if evidence.g3_trace:
        payload["g3_trace"] = evidence.g3_trace
    if not include_simulation_telemetry:
        for key in _SIMULATION_KEYS:
            payload.pop(key, None)
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

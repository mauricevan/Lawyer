"""Run dual-branch evaluation for explicit multi-part legal questions."""
from __future__ import annotations

from typing import TYPE_CHECKING, Any

from backend.src.services.combination_path_detector_service import CombinationPlan
from backend.src.utils.combination_path_formatter import format_combination_answer
from backend.src.utils.hypothesis_plan_merge import merge_case_analysis_into_plan
from backend.src.utils.hypothesis_retrieval_query import build_analysis_retrieval_query
from shared.schemas.evidence_validation import EvidenceValidationResult
from shared.schemas.legal_conflict import LegalCaseAnalysis, ReconciliationResult
from shared.schemas.legal_hypothesis import LegalHypothesis
from shared.schemas.legal_interpretation import AgentFetchResult, LegalInterpretationPlan
from shared.schemas.query import QueryRequest

if TYPE_CHECKING:
    from backend.src.services.agent_v4_pipeline_service import AgentV4PipelineService


class CombinationPathHandlerService:
    """Evaluate each combination part on its own branch without silent merge."""

    def __init__(self, pipeline: AgentV4PipelineService) -> None:
        self._pipeline = pipeline

    async def run(
        self,
        request: QueryRequest,
        history: list[dict] | None,
        session: Any,
        plan: CombinationPlan,
    ) -> tuple[
        LegalInterpretationPlan,
        AgentFetchResult,
        dict[str, Any],
        LegalHypothesis,
        EvidenceValidationResult,
        ReconciliationResult,
        LegalCaseAnalysis,
    ]:
        """Execute combination path and return pipeline-compatible tuple."""
        part_results: list[dict[str, Any]] = []
        last_analysis = LegalCaseAnalysis(
            case_summary=plan.original_question,
            context="combination_path",
            primary_legal_conflict="platform_governance_issue",
            legal_domain="data_protection",
            legal_question_type="obligations",
        )
        for part in plan.parts:
            part_results.append(
                await self._evaluate_part(request, history, session, part.text, part.branch, part.branch_label),
            )
            last_analysis = part_results[-1]["analysis"]
        bundle_raw = self._merge_bundle(request, plan, part_results)
        hypothesis = LegalHypothesis(legal_problem=plan.original_question, source="rule")
        last = part_results[-1]
        fetch = last.get("fetch") or AgentFetchResult(chunks=[], fetch_ok=False, fetch_attempted=False)
        evidence = last.get("evidence") or EvidenceValidationResult(
            is_valid=False,
            reasons=["combination_partial_gap"],
        )
        resolved = last.get("resolved") or LegalInterpretationPlan()
        reconciliation = ReconciliationResult(
            conclusion="supported" if bundle_raw["coverage_status"] == "adequate" else "contradicted",
            rationale="Combination path — per-branch evaluation.",
        )
        engine_result = await self._pipeline._engine.run_from_draft_bundle(
            request, fetch, bundle_raw,
        )
        return (
            resolved,
            fetch,
            self._pipeline._engine.result_to_bundle(engine_result),
            hypothesis,
            evidence,
            reconciliation,
            last_analysis,
        )

    async def _evaluate_part(
        self,
        request: QueryRequest,
        history: list[dict] | None,
        session: Any,
        part_text: str,
        branch: str,
        branch_label: str,
    ) -> dict[str, Any]:
        pipeline = self._pipeline
        sub_request = request.model_copy(update={"question": part_text})
        analysis = await pipeline._case_analysis.analyze(part_text, history)  # noqa: SLF001
        if analysis.legal_domain == "unknown":
            result = await pipeline._engine.run_no_domain_gap(sub_request)  # noqa: SLF001
            gap = pipeline._engine.result_to_bundle(result)  # noqa: SLF001
            return {
                "branch": branch,
                "branch_label": branch_label,
                "part_text": part_text,
                "analysis": analysis,
                "answer_text": gap["answer_text"],
                "coverage_status": gap["coverage_status"],
                "coverage_guidance": gap.get("coverage_guidance"),
                "citations": gap["citations"],
                "disclaimer": gap["disclaimer"],
                "quality": gap["quality"],
                "fetch": None,
                "evidence": None,
                "resolved": None,
                "hop_gebruikt": "gap",
            }
        plan = await pipeline._planner.interpret(part_text, history)  # noqa: SLF001
        resolved = merge_case_analysis_into_plan(plan, analysis)
        retrieval_query = build_analysis_retrieval_query(analysis)
        resolved, _celex = await pipeline._resolve_with_conflict_celex(  # noqa: SLF001
            analysis, resolved, sub_request, retrieval_query,
        )
        fetch = await pipeline._fetcher.fetch(resolved, sub_request, session)  # noqa: SLF001
        fetch, evidence = await pipeline._evidence_gate.gate(  # noqa: SLF001
            sub_request,
            resolved,
            fetch,
            session,
            pipeline._enrich_hypothesis(pipeline._case_analysis.to_hypothesis(analysis)),  # noqa: SLF001
            analysis,
            _celex,
            history,
        )
        reconciliation = pipeline._reconciliation.reconcile(analysis, fetch.chunks, evidence)  # noqa: SLF001
        engine_result, _ = await pipeline._engine.run(  # noqa: SLF001
            sub_request, fetch, resolved, history, evidence, reconciliation, analysis,
        )
        bundle = pipeline._engine.result_to_bundle(engine_result)  # noqa: SLF001
        hop = "primair" if bundle["coverage_status"] == "adequate" and evidence.is_valid else "gap"
        return {
            "branch": branch,
            "branch_label": branch_label,
            "part_text": part_text,
            "analysis": analysis,
            "answer_text": bundle["answer_text"],
            "coverage_status": bundle["coverage_status"],
            "coverage_guidance": bundle.get("coverage_guidance"),
            "citations": bundle["citations"],
            "disclaimer": bundle["disclaimer"],
            "quality": bundle["quality"],
            "fetch": fetch,
            "evidence": evidence,
            "resolved": resolved,
            "hop_gebruikt": hop,
            "evidence_valid": evidence.is_valid,
            "chunk_count": len(fetch.chunks),
        }

    def _merge_bundle(
        self,
        request: QueryRequest,
        plan: CombinationPlan,
        part_results: list[dict[str, Any]],
    ) -> dict[str, Any]:
        combined_text = format_combination_answer(part_results)
        statuses = [p["coverage_status"] for p in part_results]
        coverage_status = "adequate" if all(s == "adequate" for s in statuses) else "insufficient"
        citations = [c for p in part_results for c in p.get("citations", [])]
        base = part_results[0]
        quality = dict(base.get("quality") or {})
        quality["confidence_score"] = min(
            float(p.get("quality", {}).get("confidence_score") or 0.5)
            for p in part_results
        )
        return {
            "answer_text": combined_text,
            "citations": citations[:8],
            "disclaimer": base.get("disclaimer", ""),
            "quality": quality,
            "coverage_guidance": base.get("coverage_guidance"),
            "coverage_status": coverage_status,
            "combination_path": True,
            "combination_results": [
                {
                    "branch": p["branch"],
                    "branch_label": p["branch_label"],
                    "part_text": p["part_text"],
                    "coverage_status": p["coverage_status"],
                    "hop_gebruikt": p["hop_gebruikt"],
                    "evidence_valid": p.get("evidence_valid"),
                    "chunk_count": p.get("chunk_count", 0),
                }
                for p in part_results
            ],
            "combination_split_marker": plan.split_marker,
        }

"""EXP-002 reranker A/B promotion gate logic."""
from typing import Any

from backend.src.utils.reranker_config import experiment_thresholds


class RerankerExperimentService:
    """Evaluates whether a candidate reranker variant may be promoted."""

    def evaluate_promotion_gate(
        self,
        control: dict[str, Any],
        candidate: dict[str, Any],
    ) -> dict[str, Any]:
        thresholds = experiment_thresholds()
        mrr_delta = float(candidate["mrr"]) - float(control["mrr"])
        recall_delta = float(candidate["recall_at_5"]) - float(control["recall_at_5"])
        reasons: list[str] = []
        passed = True

        if float(candidate["p95_retrieval_ms"]) > thresholds["p95_retrieval_ms_max"]:
            passed = False
            reasons.append("candidate p95 retrieval latency above budget")

        if recall_delta < -thresholds["recall_regression_max"]:
            passed = False
            reasons.append("candidate recall regressed beyond tolerance")

        if float(control["mrr"]) >= thresholds["mrr_ceiling"]:
            if float(candidate["mrr"]) + 1e-9 < float(control["mrr"]):
                passed = False
                reasons.append("candidate MRR regressed at baseline ceiling")
        elif mrr_delta < thresholds["mrr_lift_min"]:
            passed = False
            reasons.append("candidate MRR lift below minimum")

        return {
            "passed": passed,
            "mrr_delta": mrr_delta,
            "recall_delta": recall_delta,
            "reasons": reasons,
            "thresholds": thresholds,
        }

"""Unit tests for retrieval metric helpers."""
from backend.src.utils.retrieval_metrics import mean_reciprocal_rank, recall_at_k, summarize_eval_results


def test_recall_at_k_detects_expected_celex():
    assert recall_at_k({"32024R1689"}, ["32022R2554", "32024R1689", "32016R0679"], k=5) == 1.0
    assert recall_at_k({"32024R1689"}, ["32022R2554", "32016R0679"], k=5) == 0.0


def test_mean_reciprocal_rank_uses_first_hit_rank():
    assert mean_reciprocal_rank({"32024R1689"}, ["32022R2554", "32024R1689"]) == 0.5


def test_summarize_eval_results_averages_scores():
    summary = summarize_eval_results([
        {"recall_at_5": 1.0, "mrr": 1.0},
        {"recall_at_5": 0.0, "mrr": 0.0},
    ])
    assert summary["recall_at_5"] == 0.5
    assert summary["mrr"] == 0.5
    assert summary["count"] == 2.0

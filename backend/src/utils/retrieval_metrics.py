"""Retrieval quality metrics for evaluation sets."""
from typing import Any


def recall_at_k(expected: set[str], retrieved: list[str], k: int = 5) -> float:
    """Return 1.0 when any expected CELEX appears in top-k retrieved IDs."""
    top_k = set(retrieved[:k])
    return 1.0 if expected.intersection(top_k) else 0.0


def mean_reciprocal_rank(expected: set[str], retrieved: list[str]) -> float:
    """Compute reciprocal rank for first expected CELEX hit."""
    for rank, celex in enumerate(retrieved, start=1):
        if celex in expected:
            return 1.0 / rank
    return 0.0


def summarize_eval_results(results: list[dict[str, Any]]) -> dict[str, float]:
    """Aggregate recall@5 and MRR across eval rows."""
    if not results:
        return {"recall_at_5": 0.0, "mrr": 0.0, "count": 0.0}
    recall_scores = [row["recall_at_5"] for row in results]
    mrr_scores = [row["mrr"] for row in results]
    count = len(results)
    return {
        "recall_at_5": sum(recall_scores) / count,
        "mrr": sum(mrr_scores) / count,
        "count": float(count),
    }

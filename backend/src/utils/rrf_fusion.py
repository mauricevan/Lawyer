"""Reciprocal Rank Fusion for combining ranked retrieval lists."""
from typing import Any

DEFAULT_RRF_K = 60


def reciprocal_rank_fusion(
    *ranked_lists: list[dict[str, Any]],
    k: int = DEFAULT_RRF_K,
) -> list[dict[str, Any]]:
    """Merge ranked chunk lists using RRF scoring."""
    scores: dict[str, float] = {}
    payloads: dict[str, dict[str, Any]] = {}

    for ranked in ranked_lists:
        for rank, item in enumerate(ranked, start=1):
            chunk_id = item.get("chunk_id")
            if not chunk_id:
                continue
            scores[chunk_id] = scores.get(chunk_id, 0.0) + (1.0 / (k + rank))
            payloads[chunk_id] = item

    fused = sorted(scores.items(), key=lambda pair: pair[1], reverse=True)
    return [
        {**payloads[chunk_id], "score": score, "rrf_score": score}
        for chunk_id, score in fused
    ]

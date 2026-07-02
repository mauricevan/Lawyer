"""Unit tests for reciprocal rank fusion."""
from backend.src.utils.rrf_fusion import reciprocal_rank_fusion


def test_rrf_promotes_chunks_present_in_multiple_lists():
    list_a = [{"chunk_id": "a", "text": "alpha"}, {"chunk_id": "b", "text": "beta"}]
    list_b = [{"chunk_id": "b", "text": "beta"}, {"chunk_id": "c", "text": "gamma"}]
    fused = reciprocal_rank_fusion(list_a, list_b, k=60)
    assert [item["chunk_id"] for item in fused[:2]] == ["b", "a"]


def test_rrf_preserves_payload_fields():
    fused = reciprocal_rank_fusion([{"chunk_id": "x", "celex": "32022R2554"}], k=60)
    assert fused[0]["celex"] == "32022R2554"
    assert fused[0]["rrf_score"] > 0

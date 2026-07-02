"""Unit tests for lexical BM25 ranking."""
from backend.src.services.bm25_service import Bm25Service


def test_bm25_ranks_matching_candidate_higher():
    service = Bm25Service()
    candidates = [
        {"chunk_id": "1", "text": "Algemene privacyverordening en gegevensbescherming"},
        {"chunk_id": "2", "text": "Mededingingsregels voor banken"},
    ]
    ranked = service.rank("privacy gegevensbescherming", candidates, top_k=2)
    assert ranked[0]["chunk_id"] == "1"
    assert ranked[0]["bm25_score"] > 0

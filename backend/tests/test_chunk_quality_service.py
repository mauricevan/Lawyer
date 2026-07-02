"""Tests for chunk quality filtering."""
from backend.src.services.chunk_quality_service import ChunkQualityService


def test_rejects_short_chunks():
    service = ChunkQualityService()
    chunks = [{"text": "short", "chunk_id": "1"}]
    assert service.filter_chunks(chunks) == []


def test_accepts_valid_legal_chunk():
    service = ChunkQualityService()
    text = "Financial entities shall maintain ICT risk management frameworks with documented policies."
    chunks = [{"text": text, "chunk_id": "1"}]
    assert len(service.filter_chunks(chunks)) == 1

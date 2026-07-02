"""Tests for retrieval context deduplication."""
from backend.src.utils.context_dedup import deduplicate_chunks


def test_deduplicate_by_chunk_id_and_text():
    chunks = [
        {"chunk_id": "a", "text": "Same legal text about DORA requirements for banks."},
        {"chunk_id": "a", "text": "Same legal text about DORA requirements for banks."},
        {"chunk_id": "b", "text": "Different legal text about CSRD reporting obligations."},
    ]
    result = deduplicate_chunks(chunks, max_chunks=8)
    assert len(result) == 2

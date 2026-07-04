"""Tests for legal_question_type chunk ranking."""
from backend.src.utils.legal_question_type_chunk_scoring import (
    filter_chunks_for_question_type_retry,
    rank_chunks_by_question_type,
)


def test_enforcement_prefers_surveillance_over_customs():
    chunks = [
        {"text": "Douaneautoriteit en douaneregeling via informatie- en communicatiesysteem."},
        {"text": "Markttoezichtautoriteit treft corrigerende maatregelen bij non-conform product."},
    ]
    ranked = rank_chunks_by_question_type(chunks, "enforcement")
    assert "markttoezicht" in ranked[0]["text"].lower()


def test_national_measure_prefers_harmonisation():
    chunks = [
        {"text": "Invoerrechten en douaneautoriteit."},
        {"text": "Een lidstaat mag geen nationale maatregel nemen die afwijkt van harmonisatie."},
    ]
    ranked = rank_chunks_by_question_type(chunks, "national_measure")
    assert "lidstaat" in ranked[0]["text"].lower()


def test_retry_filter_drops_negative_enforcement_noise():
    chunks = [
        {"text": "Douaneautoriteit en douaneregeling."},
        {"text": "Markttoezicht en terugroeping van de markt."},
    ]
    kept = filter_chunks_for_question_type_retry(chunks, "enforcement")
    assert any("markttoezicht" in c["text"].lower() for c in kept)

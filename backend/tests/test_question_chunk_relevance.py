"""Tests for question-chunk relevance checks."""
from backend.src.utils.question_chunk_relevance import question_matches_chunks


def test_matches_when_hint_celex_in_chunks():
    question = "Moet elke website een cookiebanner tonen?"
    chunks = [{
        "celex": "32002L0058",
        "text": "Toestemming voor cookies is vereist voor niet-noodzakelijke tracking. " * 8,
        "score": 0.8,
    }]
    assert question_matches_chunks(question, chunks)


def test_no_match_when_chunks_irrelevant():
    question = "Mijn vlucht had 5 uur vertraging."
    chunks = [{"celex": "32017R1129", "text": "Prospectus openbare aanbieding.", "score": 0.8}]
    assert not question_matches_chunks(question, chunks)


def test_empty_chunks_do_not_match():
    assert not question_matches_chunks("Wat is GDPR?", [])

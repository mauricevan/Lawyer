"""Tests for article chunk filtering."""
from backend.src.utils.article_chunk_filter import filter_chunks_by_articles


def test_filter_keeps_matching_articles_only():
    chunks = [
        {"article_number": "1", "text": "intro"},
        {"article_number": "116", "text": "terugbetaling"},
        {"article_number": "117", "text": "andere"},
    ]
    filtered = filter_chunks_by_articles(chunks, ("116", "117"))
    assert len(filtered) == 2
    assert {c["article_number"] for c in filtered} == {"116", "117"}


def test_filter_returns_original_when_no_match():
    chunks = [{"article_number": "1", "text": "x"}]
    assert filter_chunks_by_articles(chunks, ("116",)) == chunks

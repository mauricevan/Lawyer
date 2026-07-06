"""Tests for grouping subdivisions into article sessions."""
from backend.src.services.eurlex_document_session_service import EurlexDocumentSessionService


def test_group_articles_merges_parts():
    service = EurlexDocumentSessionService()
    subdivisions = [
        {"article_number": "4", "text": "Deel één.", "subdivision_type": "article"},
        {"article_number": "4", "text": "Deel twee.", "subdivision_type": "article"},
        {"article_number": "1", "text": "Inleiding.", "subdivision_type": "article"},
    ]
    articles = service._group_articles(subdivisions)
    assert set(articles) == {"4", "1"}
    assert "Deel één" in articles["4"].text
    assert "Deel twee" in articles["4"].text

"""Tests for in-document EUR-Lex article search."""
from backend.src.utils.in_document_search import search_articles_in_document
from shared.schemas.eurlex_document import EurlexArticle, EurlexDocumentSession


def _session() -> EurlexDocumentSession:
    return EurlexDocumentSession(
        celex="32013R0952",
        title="UCC",
        language="nl",
        articles={
            "4": EurlexArticle(
                article_number="4",
                title="Douanegebied",
                text="Het douanegebied omvat de Unie en de lidstaten België, Nederland, Duitsland.",
            ),
            "1": EurlexArticle(
                article_number="1",
                title="Onderwerp",
                text="Deze verordening stelt het douanewetboek van de Unie vast.",
            ),
        },
        article_count=2,
    )


def test_search_finds_customs_union_article():
    hits = search_articles_in_document(
        _session(),
        ("douane", "lidstaten", "unie"),
        limit=3,
    )
    assert hits
    assert hits[0].article_number == "4"
    assert "lidstaten" in hits[0].matched_terms


def test_search_article_hint_fallback():
    hits = search_articles_in_document(_session(), (), article_hints=("4",), limit=1)
    assert len(hits) == 1
    assert hits[0].article_number == "4"

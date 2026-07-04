"""Tests for fictional topic detection."""
from backend.src.utils.fictional_question_guard import has_unsupported_fictional_terms
from backend.src.utils.planned_article_cache import cached_includes_planned_articles


def test_quantum_teleportation_is_unsupported():
    chunks = [{"celex": "32013R0952", "article_number": "287", "text": "Inwerkingtreding douane verordening."}]
    assert has_unsupported_fictional_terms(
        "Welke EU-artikelen regelen quantum teleportatie in douane-entrepots?",
        chunks,
    )


def test_cache_rejected_when_planned_articles_missing():
    cached = [{"celex": "32013R0952", "article_number": "287", "text": "Inwerkingtreding " * 10}]
    assert not cached_includes_planned_articles(cached, ("121", "116"))

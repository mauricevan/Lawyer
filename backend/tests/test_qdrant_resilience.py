"""Unit tests for Qdrant resilience helpers (plan14 AB)."""
from backend.src.utils.qdrant_resilience import safe_celex_hint_search, safe_dense_search


class _RaisingQdrant:
    def search_with_language_fallback(self, *args, **kwargs):
        raise ConnectionError("down")

    def search_by_celex_with_language_fallback(self, *args, **kwargs):
        raise ConnectionError("down")


def test_safe_dense_search_returns_empty_on_failure():
    results = safe_dense_search(_RaisingQdrant(), [0.1], 10, "nl", True, None, set())
    assert results == []


def test_safe_celex_hint_search_returns_empty_on_failure():
    results = safe_celex_hint_search(_RaisingQdrant(), {"32022R2554"}, "nl", True)
    assert results == []

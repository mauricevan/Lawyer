"""Tests for Qdrant language fallback search."""
from backend.src.services.qdrant_service import QdrantService


class _RecordingQdrant(QdrantService):
    def __init__(self) -> None:
        self.calls: list[str | None] = []

    def search(
        self,
        query_vector,
        limit=50,
        language=None,
        in_force_only=True,
        filters=None,
        excluded_celex=None,
    ):
        self.calls.append(language)
        if language in {"fr", "en"}:
            return []
        return [{"chunk_id": "nl:1", "celex": "32016R0679", "language": "nl", "score": 0.9}]


def test_search_with_language_fallback_tries_nl_after_fr() -> None:
    qdrant = _RecordingQdrant()
    results = qdrant.search_with_language_fallback([0.1, 0.2], language="fr")
    assert results
    assert results[0]["language"] == "nl"
    assert "fr" in qdrant.calls
    assert "nl" in qdrant.calls

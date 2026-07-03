"""Unit tests for lexical CELEX hint fallback in RAG retrieval."""
from backend.src.services.rag_service import RagService


class _FakeQdrant:
    def __init__(self) -> None:
        self.calls: list[dict] = []

    def search_by_celex(
        self,
        celex_values: set[str],
        limit: int = 12,
        language: str | None = "nl",
        in_force_only: bool = True,
    ) -> list[dict]:
        self.calls.append(
            {
                "celex_values": celex_values,
                "limit": limit,
                "language": language,
                "in_force_only": in_force_only,
            }
        )
        return [{"chunk_id": "hint_chunk", "celex": next(iter(celex_values))}]

    def search_by_celex_with_language_fallback(
        self,
        celex_values: set[str],
        limit: int = 12,
        language: str | None = "nl",
        in_force_only: bool = True,
    ) -> list[dict]:
        return self.search_by_celex(celex_values, limit, language, in_force_only)


def test_hint_search_routes_dora_to_celex_lookup():
    rag = RagService()
    fake = _FakeQdrant()
    rag._pipeline._qdrant = fake
    hits = rag._pipeline._hint_search("Wat verandert DORA voor banken?", "nl", True, None)
    assert hits and hits[0]["celex"] == "32022R2554"
    assert fake.calls[0]["celex_values"] == {"32022R2554"}


def test_hint_search_routes_csrd_to_celex_lookup():
    rag = RagService()
    fake = _FakeQdrant()
    rag._pipeline._qdrant = fake
    hits = rag._pipeline._hint_search("Welke plichten geeft CSRD?", "nl", True, None)
    assert hits and hits[0]["celex"] == "32022L2464"
    assert fake.calls[0]["celex_values"] == {"32022L2464"}


def test_hint_search_without_keywords_returns_empty():
    rag = RagService()
    fake = _FakeQdrant()
    rag._pipeline._qdrant = fake
    hits = rag._pipeline._hint_search(
        "Wat is het verschil tussen verordening en richtlijn?", "nl", True, None,
    )
    assert hits == []
    assert fake.calls == []

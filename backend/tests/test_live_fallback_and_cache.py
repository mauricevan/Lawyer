"""Tests for live fallback and in-memory retrieval cache."""
import pytest

from backend.src.services.rag_service import RagService
from shared.schemas.query import QueryRequest


class _FakeQdrantEmpty:
    def search(self, *args, **kwargs):
        return []

    def search_by_celex(self, *args, **kwargs):
        return []

    def search_with_language_fallback(self, *args, **kwargs):
        return self.search(*args, **kwargs)

    def search_by_celex_with_language_fallback(self, *args, **kwargs):
        return self.search_by_celex(*args, **kwargs)


class _FakeReranker:
    def rerank(self, *args, **kwargs):
        return []


class _FakeRerankerLowScore:
    def rerank(self, *args, **kwargs):
        return [{"chunk_id": "local:1", "score": 0.05, "text": "weak local"}]


class _FakeLive:
    async def fallback_chunks(self, question: str, language: str = "nl", celex_hint: str | None = None):
        return [{
            "chunk_id": "live:32022R2554",
            "celex": "32022R2554",
            "title": "DORA",
            "text": "live excerpt",
            "source": "live_fallback",
        }]


@pytest.mark.asyncio
async def test_retrieve_uses_live_fallback_when_local_empty():
    rag = RagService()
    rag._qdrant = _FakeQdrantEmpty()
    rag._reranker = _FakeReranker()
    rag._live = _FakeLive()
    request = QueryRequest(
        question="Wat zegt 32022R2554?",
        audience="professional",
    )
    results, route = await rag._retrieve(request)
    assert results
    assert results[0]["source"] == "live_fallback"
    assert route == "live_fallback"


@pytest.mark.asyncio
async def test_retrieve_uses_memory_cache_after_first_call():
    rag = RagService()
    rag._qdrant = _FakeQdrantEmpty()
    rag._reranker = _FakeReranker()
    rag._live = _FakeLive()
    request = QueryRequest(
        question="Wat zegt 32022R2554?",
        audience="professional",
    )
    first_chunks, first_route = await rag._retrieve(request)
    second_chunks, second_route = await rag._retrieve(request)
    assert first_chunks == second_chunks
    assert first_route == "live_fallback"
    assert second_route == "cache"


@pytest.mark.asyncio
async def test_retrieve_uses_live_fallback_for_low_score_results():
    rag = RagService()
    rag._qdrant = _FakeQdrantEmpty()
    rag._reranker = _FakeRerankerLowScore()
    rag._live = _FakeLive()
    request = QueryRequest(
        question="Wat zegt 32022R2554?",
        audience="professional",
    )
    results, route = await rag._retrieve(request)
    assert results
    assert results[0]["source"] == "live_fallback"
    assert route == "live_fallback"

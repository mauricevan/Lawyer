"""Unit tests for document deprecation register (plan13 AC)."""
import pytest

from backend.src.services.document_deprecation_service import DocumentDeprecationService
from backend.src.services.rag_service import RagService
from backend.src.utils.qdrant_filters import build_qdrant_filter
from shared.schemas.query import QueryFilters, QueryRequest


def test_soft_deprecated_excluded_by_default():
    service = DocumentDeprecationService()
    assert service.is_excluded("32014R0330", "nl", None) is True


def test_explicit_celex_filter_allows_deprecated_lookup():
    service = DocumentDeprecationService()
    filters = QueryFilters(celex="32014R0330")
    assert service.is_excluded("32014R0330", "nl", filters) is False


def test_include_deprecated_bypasses_exclusion():
    service = DocumentDeprecationService()
    filters = QueryFilters(include_deprecated=True)
    assert service.is_excluded("32014R0330", "nl", filters) is False


def test_per_entry_allow_explicit_celex_false_blocks_lookup():
    service = DocumentDeprecationService()

    def fake_entries():
        from backend.src.utils.document_deprecation_config import DeprecationEntry
        return (
            DeprecationEntry(
                celex="32014R0330",
                language="nl",
                status="soft_deprecated",
                reason="test",
                allow_explicit_celex=False,
            ),
        )

    service.entries = fake_entries  # type: ignore[method-assign]
    filters = QueryFilters(celex="32014R0330")
    assert service.is_excluded("32014R0330", "nl", filters) is True


def test_filter_chunks_removes_deprecated():
    service = DocumentDeprecationService()
    chunks = [
        {"chunk_id": "a", "celex": "32014R0330", "language": "nl"},
        {"chunk_id": "b", "celex": "32022R2554", "language": "nl"},
    ]
    filtered = service.filter_chunks(chunks, None)
    assert len(filtered) == 1
    assert filtered[0]["celex"] == "32022R2554"


def test_qdrant_filter_excludes_deprecated_celex():
    query_filter = build_qdrant_filter(None, "nl", True, {"32014R0330"})
    assert query_filter is not None
    assert query_filter.must_not


def test_summarize_lists_registered_entries():
    summary = DocumentDeprecationService().summarize()
    assert summary["registered"] >= 1
    assert "32014R0330" in summary["search_excluded_celex"]


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
    variant = "control"
    model_id = "test"
    last_latency_ms = 0.0

    def rerank(self, *args, **kwargs):
        return []


class _FakeLiveDeprecated:
    async def fallback_chunks(self, question, language="nl", celex_hint=None, is_celex_allowed=None):
        celex = "32014R0330"
        if is_celex_allowed and not is_celex_allowed(celex, language):
            return []
        return [{
            "chunk_id": f"live:{celex}",
            "celex": celex,
            "title": "Deprecated",
            "text": "live excerpt",
            "language": language,
            "source": "live_fallback",
        }]


@pytest.mark.asyncio
async def test_live_fallback_blocked_for_deprecated_celex_in_question():
    rag = RagService()
    rag._pipeline._qdrant = _FakeQdrantEmpty()
    rag._pipeline._reranker = _FakeReranker()
    rag._pipeline._live = _FakeLiveDeprecated()
    request = QueryRequest(
        question="Wat zegt 32014R0330?",
        audience="professional",
    )
    results, route = await rag._retrieve(request)
    assert results == []
    assert route == "local"


class _FakeLiveAllowed:
    async def fallback_chunks(self, question, language="nl", celex_hint=None, is_celex_allowed=None):
        celex = "32022R2554"
        if is_celex_allowed and not is_celex_allowed(celex, language):
            return []
        return [{
            "chunk_id": f"live:{celex}",
            "celex": celex,
            "title": "DORA",
            "text": "live excerpt",
            "source": "live_fallback",
        }]


@pytest.mark.asyncio
async def test_live_fallback_allowed_for_non_deprecated_celex():
    rag = RagService()
    rag._pipeline._qdrant = _FakeQdrantEmpty()
    rag._pipeline._reranker = _FakeReranker()
    rag._pipeline._live = _FakeLiveAllowed()
    request = QueryRequest(
        question="Wat zegt 32022R2554?",
        audience="professional",
    )
    results, route = await rag._retrieve(request)
    assert results
    assert results[0]["source"] == "live_fallback"
    assert route == "live_fallback"

"""Tests for SPARQL-backed live retrieval service."""
import pytest

from backend.src.services.live_retrieval_service import LiveRetrievalService

LEGAL_HTML = (
    b"<html><body><h2>Article 1</h2>"
    b"<p>" + (b"Eerste zin met voldoende lengte voor chunking en tarief. " * 40)
    + b"</p></body></html>"
)


class _FakeSparql:
    async def fetch_work_by_celex(self, celex: str, language: str = "nl"):
        return {"title": f"Title for {celex}", "modified": "2024-01-01"}


class _FakeFetch:
    async def fetch_document(self, celex: str, language: str = "nl"):
        return LEGAL_HTML, "html", language, f"Title for {celex}"


@pytest.mark.asyncio
async def test_live_fallback_builds_chunked_results():
    service = LiveRetrievalService()
    service._sparql = _FakeSparql()
    service._document_fetch = _FakeFetch()
    chunks = await service.fallback_chunks("Wat zegt 32022R2554?", "nl", celex_hint="32022R2554")
    assert chunks
    assert chunks[0]["source"] == "live_fallback"
    assert chunks[0]["celex"] == "32022R2554"


@pytest.mark.asyncio
async def test_live_fallback_returns_empty_for_unusable_fetch():
    service = LiveRetrievalService()
    service._sparql = _FakeSparql()

    class _EmptyFetch:
        async def fetch_document(self, celex: str, language: str = "nl"):
            return None

    service._document_fetch = _EmptyFetch()
    chunks = await service.fallback_chunks("Wat zegt 32022R2554?", "nl", celex_hint="32022R2554")
    assert chunks == []

"""Tests for SPARQL-backed live retrieval service."""
import pytest

from backend.src.services.live_retrieval_service import LiveRetrievalService


class _FakeSparql:
    async def fetch_work_by_celex(self, celex: str, language: str = "nl"):
        return {"title": f"Title for {celex}", "modified": "2024-01-01"}


@pytest.mark.asyncio
async def test_live_fallback_builds_chunked_results(monkeypatch):
    service = LiveRetrievalService()
    service._sparql = _FakeSparql()

    async def fake_fetch_document_html(celex: str, language: str):
        html = (
            b"<html><body><h2>Article 1</h2>"
            b"<p>Eerste zin met voldoende lengte voor chunking. Tweede zin met ook voldoende lengte voor chunking.</p>"
            b"</body></html>"
        )
        return "HTML title", html

    service._fetch_document_html = fake_fetch_document_html  # type: ignore[method-assign]
    chunks = await service.fallback_chunks("Wat zegt 32022R2554?", "nl", celex_hint="32022R2554")
    assert chunks
    assert chunks[0]["source"] == "live_fallback"
    assert chunks[0]["celex"] == "32022R2554"
    assert "Title for" in chunks[0]["title"]

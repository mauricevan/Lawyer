"""Tests for corpus summary API (blueprint §7 trust indicator)."""
import pytest
from httpx import ASGITransport, AsyncClient

from backend.src.main import app


@pytest.mark.asyncio
async def test_corpus_summary_is_public():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/v1/documents/corpus/summary")
    assert response.status_code == 200
    body = response.json()
    assert "documents_indexed" in body
    assert "chunks_indexed" in body
    assert "vector_points" in body

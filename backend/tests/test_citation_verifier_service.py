"""Tests for citation verifier deterministic checks."""
import pytest

from backend.src.services.citation_verifier_service import CitationVerifierService


@pytest.mark.asyncio
async def test_rejects_article_not_in_chunks(monkeypatch):
    async def mock_llm(*_args, **_kwargs):
        return {"supported": True, "unsupported_claims": []}

    monkeypatch.setattr(
        "backend.src.services.citation_verifier_service.call_llm_json",
        mock_llm,
    )
    verifier = CitationVerifierService()
    chunks = [{"celex": "32006R1907", "article_number": "6", "text": "registratie"}]
    answer = "Volgens artikel 99 moet u registreren."
    supported, _text, issues = await verifier.verify(answer, chunks)
    assert supported is False
    assert issues


@pytest.mark.asyncio
async def test_accepts_supported_article_reference(monkeypatch):
    async def mock_llm(*_args, **_kwargs):
        return {"supported": True, "unsupported_claims": []}

    monkeypatch.setattr(
        "backend.src.services.citation_verifier_service.call_llm_json",
        mock_llm,
    )
    verifier = CitationVerifierService()
    chunks = [{"celex": "32006R1907", "article_number": "6", "text": "registratie verplicht"}]
    answer = "Artikel 6 vereist registratie."
    supported, _text, issues = await verifier.verify(answer, chunks)
    assert supported is True
    assert not issues

"""Tests for article fetch orchestrator."""
import pytest

from backend.src.services.article_fetch_orchestrator_service import ArticleFetchOrchestratorService
from shared.schemas.legal_interpretation import InstrumentTarget, LegalInterpretationPlan
from shared.schemas.query import QueryRequest


@pytest.mark.asyncio
async def test_fetch_merges_parallel_instruments(monkeypatch):
    orchestrator = ArticleFetchOrchestratorService()

    async def mock_live(*_args, **_kwargs):
        celex = _kwargs.get("celex_hint")
        text = (
            f"Artikel 1 toepassing van CELEX {celex} met verplichtingen voor marktdeelnemers "
            "en exploitanten onder de EU-regelgeving."
        ) * 3
        return [{
            "chunk_id": f"live:{celex}:1",
            "celex": celex,
            "language": "nl",
            "article_number": "1",
            "text": text,
        }]

    monkeypatch.setattr(orchestrator._live, "fallback_chunks", mock_live)
    monkeypatch.setattr(orchestrator._qdrant, "search_by_celex", lambda *_a, **_k: [])
    plan = LegalInterpretationPlan(
        instruments=[
            InstrumentTarget(name="A", celex="32006R1907", articles=[], confidence=0.9),
            InstrumentTarget(name="B", celex="32004L0035", articles=[], confidence=0.8),
        ],
    )
    request = QueryRequest(question="test", language="nl")
    result = await orchestrator.fetch(plan, request)
    assert result.fetch_ok is True
    assert len(result.chunks) == 2
    assert set(result.resolved_celex) == {"32006R1907", "32004L0035"}


@pytest.mark.asyncio
async def test_cache_hit_skips_live(monkeypatch):
    orchestrator = ArticleFetchOrchestratorService()
    cached = [{
        "chunk_id": "c1",
        "celex": "32006R1907",
        "language": "nl",
        "article_number": "6",
        "text": "Registratie van stoffen onder REACH vereist documentatie en veiligheidsinformatie van de fabrikant." * 3,
    }]
    monkeypatch.setattr(
        orchestrator._qdrant,
        "search_by_celex",
        lambda *_a, **_k: cached,
    )

    async def fail_live(*_args, **_kwargs):
        raise AssertionError("live should not be called on cache hit")

    monkeypatch.setattr(orchestrator._live, "fallback_chunks", fail_live)
    plan = LegalInterpretationPlan(
        instruments=[InstrumentTarget(name="REACH", celex="32006R1907", articles=["6"], confidence=0.9)],
    )
    request = QueryRequest(question="REACH registratie", language="nl")
    result = await orchestrator.fetch(plan, request)
    assert result.fetch_source == "cache"
    assert result.chunks[0]["article_number"] == "6"


@pytest.mark.asyncio
async def test_cache_skips_english_when_dutch_requested(monkeypatch):
    orchestrator = ArticleFetchOrchestratorService()
    english_only = [{
        "chunk_id": "en:1",
        "celex": "32004L0035",
        "language": "en",
        "title": "EUR-Lex - 32004L0035 - EN",
        "article_number": "3",
        "text": (
            "This Directive shall apply to environmental damage caused by occupational "
            "activities listed in Annex III and operators shall take preventive action."
        ) * 3,
    }]

    def strict_search(*_args, **kwargs):
        language = kwargs.get("language")
        return english_only if language == "en" else []

    monkeypatch.setattr(orchestrator._qdrant, "search_by_celex", strict_search)
    monkeypatch.setattr(
        orchestrator._qdrant,
        "search_by_celex_with_language_fallback",
        lambda *_a, **_k: english_only,
    )

    async def mock_live(*_args, **_kwargs):
        return [{
            "chunk_id": "live:nl:1",
            "celex": "32004L0035",
            "language": "nl",
            "title": "EUR-Lex - 32004L0035 - NL",
            "article_number": "5",
            "text": (
                "De exploitant neemt onverwijld de nodige preventieve maatregelen wanneer "
                "milieuschade dreigt te ontstaan en stelt de bevoegde instantie in kennis."
            ) * 3,
        }]

    monkeypatch.setattr(orchestrator._live, "fallback_chunks", mock_live)
    plan = LegalInterpretationPlan(
        instruments=[InstrumentTarget(name="ELD", celex="32004L0035", articles=["5"], confidence=0.9)],
    )
    request = QueryRequest(question="milieuaansprakelijkheid exploitant", language="nl")
    result = await orchestrator.fetch(plan, request)
    assert result.fetch_source == "live"
    assert result.chunks[0]["language"] == "nl"
    assert "exploitant" in result.chunks[0]["text"].lower()

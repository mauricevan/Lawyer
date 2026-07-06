"""Tests for EUR-Lex research fetch orchestration."""
from unittest.mock import AsyncMock, patch

import pytest

from backend.src.services.article_fetch_orchestrator_service import ArticleFetchOrchestratorService
from shared.schemas.legal_interpretation import AgentFetchResult, InstrumentTarget, LegalInterpretationPlan
from shared.schemas.query import QueryRequest


@pytest.mark.asyncio
async def test_fetch_uses_research_path_when_enabled():
    plan = LegalInterpretationPlan(
        instruments=[InstrumentTarget(name="UCC", celex="32013R0952", articles=("4",))],
        search_keywords=("douane", "unie"),
    )
    request = QueryRequest(
        question="Welke lidstaten doen mee aan de douane-unie?",
        audience="layperson",
        language="nl",
    )
    expected = AgentFetchResult(
        chunks=[{"celex": "32013R0952", "article_number": "4", "text": "lidstaten", "source": "eurlex_research"}],
        fetch_ok=True,
        fetch_source="eurlex_research",
    )
    with patch.object(
        ArticleFetchOrchestratorService,
        "__init__",
        lambda self: None,
    ):
        orchestrator = ArticleFetchOrchestratorService.__new__(ArticleFetchOrchestratorService)
        orchestrator._research = AsyncMock()
        orchestrator._research.fetch = AsyncMock(return_value=expected)
        with patch("backend.src.services.article_fetch_orchestrator_service.settings") as mock_settings:
            mock_settings.eurlex_research_agent_enabled = True
            mock_settings.enable_live_fallback = True
            result = await orchestrator.fetch(plan, request)
    assert result.fetch_source == "eurlex_research"
    assert result.chunks[0]["article_number"] == "4"

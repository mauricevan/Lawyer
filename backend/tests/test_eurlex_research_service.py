"""Integration tests for EurlexResearchService with mocked live sessions."""
from unittest.mock import AsyncMock, patch

import pytest

from backend.src.services.eurlex_research_service import EurlexResearchService
from shared.schemas.eurlex_document import EurlexArticle, EurlexDocumentSession
from shared.schemas.legal_interpretation import InstrumentTarget, LegalInterpretationPlan
from shared.schemas.query import QueryRequest


def _ucc_session() -> EurlexDocumentSession:
    return EurlexDocumentSession(
        celex="32013R0952",
        title="Douanewetboek van de Unie",
        language="nl",
        articles={
            "4": EurlexArticle(
                article_number="4",
                title="Douanegebied",
                text=(
                    "Het douanegebied omvat de Unie, de lidstaten en de "
                    "andere gebieden die in bijlage I zijn vermeld."
                ),
            ),
        },
        article_count=1,
    )


@pytest.mark.asyncio
async def test_research_returns_live_article_chunks():
    plan = LegalInterpretationPlan(
        instruments=[InstrumentTarget(name="UCC", celex="32013R0952", articles=["4"])],
        search_keywords=["douane", "unie", "lidstaten"],
        legal_domain="customs_law",
    )
    request = QueryRequest(
        question="Welke Europese lidstaten doen mee aan de douane-unie?",
        audience="layperson",
        language="nl",
    )
    service = EurlexResearchService()
    with patch.object(service._sessions, "load", AsyncMock(return_value=_ucc_session())):
        result = await service.fetch(plan, request)
    assert result.fetch_ok
    assert result.fetch_source == "eurlex_research"
    assert result.chunks
    assert result.chunks[0]["celex"] == "32013R0952"
    assert result.chunks[0]["article_number"] == "4"
    assert result.chunks[0]["source"] == "eurlex_research"

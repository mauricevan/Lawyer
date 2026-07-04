"""Tests for layperson gap policy and agent clear-answer fallback."""
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from backend.src.services.agent_answer_service import AgentAnswerService
from backend.src.services.layperson_obligation_fallback_service import LaypersonObligationFallbackService
from backend.src.utils.layperson_gap_policy import is_publishable_clear_answer
from shared.schemas.legal_interpretation import AgentFetchResult, LegalInterpretationPlan
from shared.schemas.query import QueryRequest

EMPLOYMENT_QUESTION = (
    "Een werknemer in de EU wordt ontslagen terwijl hij langdurig ziek is. "
    "Welke EU-regels zijn relevant voor de bescherming tegen discriminatie op "
    "grond van handicap of gezondheid, en welke rechten kan de werknemer "
    "hieraan ontlenen?"
)
CLEAR_SAMPLE = LaypersonObligationFallbackService().compose(EMPLOYMENT_QUESTION, [])


def test_template_fallback_produces_publishable_answer():
    assert CLEAR_SAMPLE is not None
    assert is_publishable_clear_answer(CLEAR_SAMPLE)


def test_publishable_clear_answer_requires_all_sections():
    assert not is_publishable_clear_answer("## Kort antwoord\nKort.")
    assert not is_publishable_clear_answer(
        "## Kort antwoord\nJa.\n\n## Gedeeltelijk antwoord\n## Kort antwoord\nJa."
    )


@pytest.mark.asyncio
async def test_fetch_attempted_uses_template_fallback_without_gap_wrapper():
    service = AgentAnswerService()
    request = QueryRequest(question=EMPLOYMENT_QUESTION, audience="layperson", language="nl")
    plan = LegalInterpretationPlan(
        legal_actor="employee",
        legal_issue="obligation",
        instruments=[],
    )
    fetch = AgentFetchResult(chunks=[], fetch_attempted=True, attempted_celex=["32000L0078"])
    bundle = await service.build(request, fetch, plan, None)
    answer = bundle["answer_text"]
    assert "kon op dit moment geen betrouwbare" not in answer
    assert "Gedeeltelijk antwoord" not in answer
    assert answer.count("## Kort antwoord") == 1
    assert "## Voorbeeld" in answer


@pytest.mark.asyncio
async def test_verify_fail_prefers_clear_fallback_over_gap():
    service = AgentAnswerService()
    request = QueryRequest(question=EMPLOYMENT_QUESTION, audience="layperson", language="nl")
    plan = LegalInterpretationPlan(legal_actor="employee", legal_issue="obligation")
    chunks = [{"text": "nav noise", "celex": "32000L0078", "article_number": "1"}]

    with patch.object(service._llm, "generate_answer", new=AsyncMock(return_value=("bad", []))):
        with patch.object(service._verifier, "verify", new=AsyncMock(return_value=(False, "bad", []))):
            bundle = await service._answer_from_chunks(
                request, chunks, plan, None, "agent_flow", MagicMock(),
            )
    assert "Gedeeltelijk antwoord" not in bundle["answer_text"]
    assert bundle["answer_text"].count("## Kort antwoord") == 1

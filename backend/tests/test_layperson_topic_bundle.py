"""Tests for layperson topic template bundles."""
import pytest

from backend.src.services.answer_bundle_service import AnswerBundleService
from shared.schemas.query import QueryRequest


@pytest.mark.asyncio
async def test_flight_question_uses_topic_template():
    request = QueryRequest(
        question="Mijn vlucht binnen Europa had 5 uur vertraging. Heb ik recht op compensatie?",
        audience="layperson",
    )
    bundle = await AnswerBundleService().build(request, [], "cache", None)
    assert bundle["coverage_status"] == "adequate"
    assert bundle["retrieval_route"] == "layperson_topic"
    assert "compensatie" in bundle["answer_text"].lower()
    assert "32004R0261" not in bundle["answer_text"]
    assert bundle["citations"]


@pytest.mark.asyncio
async def test_cookie_question_uses_topic_template():
    request = QueryRequest(
        question="Moet elke website in Europa een cookiebanner tonen?",
        audience="layperson",
    )
    bundle = await AnswerBundleService().build(request, [], "cache", None)
    assert bundle["coverage_status"] == "adequate"
    assert "cookie" in bundle["answer_text"].lower()
    assert "## Kort antwoord" in bundle["answer_text"]


@pytest.mark.asyncio
async def test_llm_fallback_formatted_for_layperson():
    from backend.src.services.llm_service import LlmService

    chunks = [{
        "title": "AVG",
        "text": "Artikel 6. Verwerking is rechtmatig wanneer de betrokkene toestemming heeft gegeven.",
        "celex": "32016R0679",
        "score": 0.9,
    }]
    answer = LlmService()._fallback_answer("Mag mijn werkgever e-mails lezen?", chunks, "layperson")
    assert "lijkt artikel" not in answer.lower()
    assert "CELEX" not in answer
    assert "## Kort antwoord" in answer
    assert "## Uitleg" in answer

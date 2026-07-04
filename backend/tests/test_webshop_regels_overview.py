"""Regression: webshop + AVG + consument must not fall through to workplace gap."""
import pytest

from backend.src.services.answer_bundle_service import AnswerBundleService
from backend.src.services.layperson_topic_service import LaypersonTopicService
from shared.schemas.query import QueryRequest

WEBSHOP_QUESTION = (
    "Welke EU-regels zijn van toepassing op een webshop die persoonsgegevens verwerkt "
    "én producten aan consumenten verkoopt?"
)


def test_webshop_overview_topic_matches():
    match = LaypersonTopicService().match(WEBSHOP_QUESTION)
    assert match is not None
    assert match.topic_id == "webshop_regels_overzicht"


@pytest.mark.asyncio
async def test_webshop_overview_returns_adequate_topic_answer():
    request = QueryRequest(question=WEBSHOP_QUESTION, audience="layperson", language="nl")
    bundle = await AnswerBundleService().build(request, [], "layperson_topic", None)
    assert bundle["coverage_status"] == "adequate"
    answer = bundle["answer_text"].lower()
    assert "avg" in answer or "gdpr" in answer
    assert "consument" in answer
    assert "kon geen betrouwbaar antwoord" not in answer

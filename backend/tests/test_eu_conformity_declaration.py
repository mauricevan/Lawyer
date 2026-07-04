"""Regression: EU conformity declaration questions must not gap."""
import pytest

from backend.src.services.answer_bundle_service import AnswerBundleService
from backend.src.services.layperson_topic_service import LaypersonTopicService
from shared.schemas.query import QueryRequest

QUESTION = (
    "Welke informatie moet een fabrikant opnemen in de EU-conformiteitsverklaring "
    "volgens de toepasselijke harmonisatiewetgeving?"
)


def test_conformity_declaration_topic_matches():
    match = LaypersonTopicService().match(QUESTION)
    assert match is not None
    assert match.topic_id == "eu_conformity_declaration"


@pytest.mark.asyncio
async def test_conformity_declaration_returns_adequate_answer():
    request = QueryRequest(question=QUESTION, audience="layperson", language="nl")
    bundle = await AnswerBundleService().build(request, [], "layperson_topic", None)
    assert bundle["coverage_status"] == "adequate"
    answer = bundle["answer_text"].lower()
    assert "fabrikant" in answer
    assert "harmonisatie" in answer or "conformiteit" in answer
    assert "kon geen betrouwbaar antwoord" not in answer

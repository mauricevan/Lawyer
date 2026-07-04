"""Regression tests: layperson topics must not be blocked by broad intent triggers."""
import pytest

from backend.src.services.answer_bundle_service import AnswerBundleService
from shared.schemas.query import QueryRequest

N06 = (
    "Ik bestelde eten via Deliveroo en werd ziek. "
    "Kan ik de verkoper aansprakelijk stellen volgens EU-recht?"
)
N07 = "Mijn telefoonabonnement loopt 3 jaar. Mag de provider me vastzetten volgens EU-regels?"
N13 = "Mag ik met mijn Nederlandse rijbewijs in Italië rijden volgens EU-regels?"
GENERIC_UCC = "Wat regelt Verordening (EU) nr. 952/2013?"


@pytest.mark.asyncio
async def test_n06_deliveroo_uses_layperson_topic():
    bundle = await AnswerBundleService().build(
        QueryRequest(question=N06, audience="layperson", language="nl"), [], "cache", None,
    )
    assert bundle["retrieval_route"] == "layperson_topic"
    assert bundle["coverage_status"] == "adequate"
    assert "kon geen specifieke wettekst" not in bundle["answer_text"].lower()


@pytest.mark.asyncio
async def test_n07_telecom_uses_layperson_topic():
    bundle = await AnswerBundleService().build(
        QueryRequest(question=N07, audience="layperson", language="nl"), [], "cache", None,
    )
    assert bundle["retrieval_route"] == "layperson_topic"
    assert bundle["coverage_status"] == "adequate"


@pytest.mark.asyncio
async def test_n13_driving_license_uses_layperson_topic():
    bundle = await AnswerBundleService().build(
        QueryRequest(question=N13, audience="layperson", language="nl"), [], "cache", None,
    )
    assert bundle["retrieval_route"] == "layperson_topic"
    assert bundle["coverage_status"] == "adequate"


@pytest.mark.asyncio
async def test_generic_ucc_uses_registry_intro_topic():
    bundle = await AnswerBundleService().build(
        QueryRequest(question=GENERIC_UCC, audience="layperson", language="nl"), [], "cache", None,
    )
    assert bundle["retrieval_route"] == "layperson_topic"
    assert bundle["coverage_status"] == "adequate"


@pytest.mark.asyncio
async def test_article_lookup_professional_skips_customs_intro():
    question = (
        "Mag een bedrijf een invoeraangifte wijzigen nadat de goederen zijn vrijgegeven? "
        "Noem de relevante artikelen."
    )
    bundle = await AnswerBundleService().build(
        QueryRequest(
            question=question, audience="professional", language="nl", query_mode="compliance",
        ),
        [], "cache", None,
    )
    assert bundle["retrieval_route"] != "layperson_topic"
    assert "moderniseert douaneprocessen" not in bundle["answer_text"].lower()

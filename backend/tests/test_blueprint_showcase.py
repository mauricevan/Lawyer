"""Blueprint showcase: product promise for procedural EU law questions."""
import pytest

from backend.src.services.answer_bundle_service import AnswerBundleService
from backend.src.services.retrieval_pipeline_service import RetrievalPipelineService
from shared.schemas.query import QueryRequest

BLUEPRINT_CUSTOMS = (
    "Een Nederlandse importeur heeft machines uit Japan ingevoerd. Na de invoer blijkt "
    "dat de douanewaarde te hoog is vastgesteld doordat een korting niet was verwerkt. "
    "Kan de importeur terugbetaling van invoerrechten krijgen? "
    "Welke voorwaarden gelden volgens het Douanewetboek van de Unie?"
)

UCC_CHUNK = {
    "chunk_id": "live:32013R0952_nl_116_0",
    "celex": "32013R0952",
    "title": "UCC",
    "text": (
        "CELEX:32013R0952 | L_2013269NL.01000101.xml | Artikel 116 | article "
        "Artikel 116 Algemene bepalingen 1. Onder de bij deze afdeling vastgestelde "
        "voorwaarden wordt overgegaan tot terugbetaling of kwijtschelding van bedragen "
        "aan invoer- of uitvoerrechten, om elk van de volgende redenen: a) invoer- of "
        "uitvoerrechten die te veel in rekening zijn gebracht."
    ),
    "article_number": "116",
    "language": "nl",
    "score": 1.0,
    "source": "live_fallback",
}


@pytest.mark.asyncio
async def test_blueprint_customs_bundle_from_ucc_chunks():
    request = QueryRequest(question=BLUEPRINT_CUSTOMS, audience="layperson", language="nl")
    bundle = await AnswerBundleService().build(request, [UCC_CHUNK], "live_fallback", None)
    assert bundle["coverage_status"] == "adequate"
    assert len(bundle["citations"]) >= 1
    answer = bundle["answer_text"].lower()
    assert "terugbetaling" in answer or "kwijtschelding" in answer
    assert "kon geen betrouwbaar antwoord" not in answer


@pytest.mark.asyncio
@pytest.mark.integration
async def test_blueprint_customs_end_to_end_live_retrieval():
    request = QueryRequest(question=BLUEPRINT_CUSTOMS, audience="layperson", language="nl")
    chunks, route, _ = await RetrievalPipelineService().retrieve(request, session=None)
    assert len(chunks) >= 1
    bundle = await AnswerBundleService().build(request, chunks, route, None)
    assert bundle["coverage_status"] == "adequate"
    assert len(bundle["citations"]) >= 1


@pytest.mark.asyncio
async def test_blueprint_customs_professional_from_ucc_chunks():
    request = QueryRequest(
        question=BLUEPRINT_CUSTOMS,
        audience="professional",
        language="nl",
        query_mode="compliance",
    )
    bundle = await AnswerBundleService().build(request, [UCC_CHUNK], "live_fallback", None)
    assert bundle["coverage_status"] == "adequate"
    assert "32013R0952" in str(bundle["citations"][0].celex)

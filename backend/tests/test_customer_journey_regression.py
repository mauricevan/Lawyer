"""Customer-journey regression gate from layperson test report."""
from unittest.mock import AsyncMock, patch

import pytest

from backend.src.services.context_adequacy_service import ContextAdequacyService
from backend.src.services.rag_service import RagService
from backend.src.services.vague_question_service import VagueQuestionService
from shared.schemas.query import QueryFilters, QueryRequest


LAYPERSON_ADEQUATE = [
    "Moet ik mijn chatbot registreren bij de overheid?",
    "Geldt de AI-wet ook voor mijn kleine webshop?",
    "Mag ik klantgegevens gebruiken om mijn AI te trainen?",
]

LAYPERSON_GAP = [
    "Mijn werkgever wil mijn Teams-chats door AI scannen. Mag dat?",
    "Hoeveel vakantiedagen heb ik volgens de Nederlandse wet?",
]

GOOD_CHUNKS = [
    {
        "chunk_id": "c1",
        "celex": "32024R1689",
        "title": "AI Act transparantie",
        "text": (
            "AI-systemen en chatbots transparantieverplichtingen voor deployers. "
            "Artikel 50 vereist registratie en informatieplichten voor bepaalde AI-systemen."
        ),
        "score": 0.62,
        "rerank_score": 0.58,
        "article_number": "50",
    }
]


def test_layperson_adequate_questions_pass_adequacy_gate() -> None:
    service = ContextAdequacyService()
    for question in LAYPERSON_ADEQUATE:
        result = service.assess(question, GOOD_CHUNKS, retrieval_route="local")
        assert result.is_adequate, f"Expected adequate for: {question}"


def test_workplace_monitoring_triggers_gap() -> None:
    service = ContextAdequacyService()
    question = LAYPERSON_GAP[0]
    irrelevant = [
        {
            "title": "Prospectusverordening",
            "text": "Openbare aanbieding van effecten.",
            "score": 0.7,
            "rerank_score": 0.65,
        }
    ]
    result = service.assess(question, irrelevant, retrieval_route="local")
    assert not result.is_adequate


def test_vague_question_is_clarify_only() -> None:
    service = VagueQuestionService()
    assert service.is_vague("Mag ik dit?")


@pytest.mark.asyncio
async def test_rag_cn_classification_uses_llm_with_live_fallback() -> None:
    rag = RagService()
    question = (
        "Als ik een paard van zuiver ras importeer onder goederen code 0101 - "
        "is de kans dan groot dat deze goederencode juist is?"
    )
    live_chunks = [{
        "celex": "31987R2658",
        "title": "Gecombineerde Nomenclatuur",
        "text": (
            "0101 Paarden, ezels, muilezels. 0101 21 00 Fokdieren van zuiver ras. "
            "Import en douaneaangifte volgens de gecombineerde nomenclatuur."
        ) * 3,
        "score": 1.0,
        "source": "live_fallback",
    }]
    request = QueryRequest(question=question, audience="layperson")
    with patch.object(rag._llm, "generate_answer", new_callable=AsyncMock) as mock_llm:
        mock_llm.return_value = ("0101 is de juiste positie voor paarden.", [])
        bundle = await rag._build_answer_bundle(request, live_chunks, "live_fallback", None)
        mock_llm.assert_called_once()
    assert bundle["coverage_status"] == "adequate"
    assert bundle["citations"]


@pytest.mark.asyncio
async def test_rag_cn_classification_fallback_without_live() -> None:
    rag = RagService()
    question = (
        "Als ik een paard van zuiver ras importeer onder goederen code 0101 - "
        "is de kans dan groot dat deze goederencode juist is?"
    )
    request = QueryRequest(question=question, audience="layperson")
    with patch.object(rag._llm, "generate_answer", new_callable=AsyncMock) as mock_llm:
        bundle = await rag._build_answer_bundle(request, [], "local", None)
        mock_llm.assert_not_called()
    assert bundle["coverage_status"] == "adequate"
    assert "0101 21 00" in bundle["answer_text"]
    assert bundle["citations"][0].celex == "31987R2658"


@pytest.mark.asyncio
async def test_rag_happy_path_calls_llm_with_good_chunks() -> None:
    rag = RagService()
    question = (
        "Welke transparantie-eisen gelden voor deployers onder artikel 50 "
        "van de AI-verordening?"
    )
    request = QueryRequest(
        question=question,
        audience="layperson",
        query_mode="compliance",
    )
    with patch.object(rag._llm, "generate_answer", new_callable=AsyncMock) as mock_llm:
        mock_llm.return_value = ("Registratie kan vereist zijn.", [])
        bundle = await rag._build_answer_bundle(request, GOOD_CHUNKS, "local", None)
        mock_llm.assert_called_once()
    assert bundle["coverage_status"] == "adequate"
    assert "none" not in bundle["answer_text"].lower()


def test_chatbot_question_hints_ai_act_celex() -> None:
    from ingestion.src.data.legal_term_hints import match_primary_celex_hint

    assert match_primary_celex_hint(LAYPERSON_ADEQUATE[0]) == "32024R1689"


def test_oj_citation_2658_resolves_to_celex() -> None:
    from ingestion.src.data.legal_term_hints import match_primary_celex_hint

    assert match_primary_celex_hint("Verordening (EEG) nr. 2658/87") == "31987R2658"


def test_modern_oj_citation_952_2013_resolves_to_celex() -> None:
    from ingestion.src.data.legal_term_hints import match_primary_celex_hint

    assert match_primary_celex_hint("Verordening (EU) nr. 952/2013") == "32013R0952"


@pytest.mark.asyncio
async def test_rag_vague_skips_llm() -> None:
    rag = RagService()
    request = QueryRequest(question="Mag ik dit?", audience="layperson")
    with patch.object(rag._llm, "generate_answer", new_callable=AsyncMock) as mock_llm:
        response, _, _ = await rag.query(request, [], session=None)
        mock_llm.assert_not_called()
    assert response.coverage_status == "clarify_only"


@pytest.mark.asyncio
async def test_rag_compare_needs_two_celex() -> None:
    rag = RagService()
    request = QueryRequest(
        question="Vergelijk GDPR artikel 6 met artikel 9",
        audience="professional",
        query_mode="compare",
    )
    single = [GOOD_CHUNKS[0]]
    with patch.object(rag._llm, "generate_answer", new_callable=AsyncMock) as mock_llm:
        bundle = await rag._build_answer_bundle(request, single, "local", None)
        mock_llm.assert_not_called()
    assert bundle["coverage_status"] != "adequate"


@pytest.mark.asyncio
async def test_intent_mismatch_stays_coverage_gap() -> None:
    rag = RagService()
    question = LAYPERSON_GAP[0]
    request = QueryRequest(
        question=question,
        audience="layperson",
        filters=QueryFilters(intent_id="INT-EMPLOYMENT-HOURS"),
    )
    chunks = [
        {
            "chunk_id": "c1",
            "celex": "32003L0088",
            "title": "Arbeidstijden",
            "text": (
                "Rusttijden en werkroosters voor werknemers volgens de arbeidstijdenrichtlijn. "
                "Artikel 3 stelt minimum rusttijden en maximum arbeidsduur per etmaal en per week."
            ),
            "score": 0.7,
            "rerank_score": 0.66,
        }
    ]
    with patch.object(rag._llm, "generate_answer", new_callable=AsyncMock) as mock_llm:
        bundle = await rag._build_answer_bundle(request, chunks, "local", None)
        mock_llm.assert_not_called()
    assert bundle["coverage_status"] == "irrelevant"

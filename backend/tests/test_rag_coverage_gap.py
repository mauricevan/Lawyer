"""Tests for RAG coverage-gap integration."""
from unittest.mock import AsyncMock, patch

import pytest

from backend.src.services.rag_service import RagService
from shared.schemas.query import QueryFilters, QueryRequest


@pytest.mark.asyncio
async def test_rag_skips_llm_on_irrelevant_retrieval() -> None:
    rag = RagService()
    question = (
        "Mijn werkgever wil mijn Teams-chats door AI scannen. Mag dat zonder toestemming?"
    )
    request = QueryRequest(
        question=question,
        audience="layperson",
        query_mode="compliance",
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

    assert "misschien" not in bundle["answer_text"].lower()
    assert bundle["coverage_guidance"] is not None
    assert bundle["coverage_status"] == "irrelevant"
    assert bundle["citations"] == []

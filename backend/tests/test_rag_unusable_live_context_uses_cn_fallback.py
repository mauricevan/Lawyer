"""RAG falls back to CN template when live chunks are unusable navigation HTML."""
from unittest.mock import AsyncMock, patch

import pytest

from backend.src.services.rag_service import RagService
from shared.schemas.query import QueryRequest

HORSE_QUESTION = (
    "Als ik een paard van zuiver ras importeer onder goederen code 0101 - "
    "is de kans dan groot dat deze goederencode juist is?"
)
NAV_CHUNKS = [{
    "celex": "31987R2658",
    "title": "EUR-Lex",
    "text": "Skip to main content My EUR-Lex sign in register please wait",
    "score": 1.0,
    "source": "live_fallback",
}]


@pytest.mark.asyncio
async def test_unusable_live_context_uses_cn_fallback() -> None:
    rag = RagService()
    request = QueryRequest(question=HORSE_QUESTION, audience="layperson")
    with patch.object(rag._llm, "generate_answer", new_callable=AsyncMock) as mock_llm:
        bundle = await rag._build_answer_bundle(request, NAV_CHUNKS, "live_fallback", None)
        mock_llm.assert_not_called()
    assert bundle["coverage_status"] == "adequate"
    assert "0101 21 00" in bundle["answer_text"]
    assert bundle["citations"][0].celex == "31987R2658"

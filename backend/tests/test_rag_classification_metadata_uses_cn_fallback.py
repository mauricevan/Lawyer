"""CN fallback when classification questions get metadata-only EUR-Lex chunks."""
from unittest.mock import AsyncMock, patch

import pytest

from backend.src.services.rag_service import RagService
from shared.schemas.query import QueryRequest

HORSE_QUESTION = (
    "Als ik een paard van zuiver ras importeer onder goederen code 0101 - "
    "is de kans dan groot dat deze goederencode juist is?"
)
METADATA_CHUNKS = [{
    "celex": "31987R2658",
    "title": "Gecombineerde Nomenclatuur",
    "text": (
        "CELEX:31987R2658 Verordening 2658/87 tarief- en statistieknomenclatuur "
        "Publicatieblad Nr. L 256 blz. 0001 - 0675 Bijzondere uitgave EUR-Lex - "
        "Avis juridique important pour le document."
    ),
    "score": 1.0,
    "source": "live_fallback",
}]


@pytest.mark.asyncio
async def test_metadata_only_classification_uses_cn_fallback() -> None:
    rag = RagService()
    request = QueryRequest(question=HORSE_QUESTION, audience="layperson")
    with patch.object(rag._llm, "generate_answer", new_callable=AsyncMock) as mock_llm:
        bundle = await rag._build_answer_bundle(request, METADATA_CHUNKS, "live_fallback", None)
        mock_llm.assert_not_called()
    assert bundle["coverage_status"] == "adequate"
    assert "0101" in bundle["answer_text"]
    assert "0101 21 00" in bundle["answer_text"]
    assert "bindende douane-classificatie" in bundle["answer_text"].lower()
    assert bundle["citations"][0].celex == "31987R2658"

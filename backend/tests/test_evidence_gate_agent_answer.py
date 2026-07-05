"""Tests for evidence gate blocking speculative answers."""
import pytest

from backend.src.services.agent_answer_service import AgentAnswerService
from shared.schemas.evidence_validation import EvidenceValidationResult
from shared.schemas.legal_interpretation import AgentFetchResult, LegalInterpretationPlan
from shared.schemas.query import QueryRequest

WEAK_CHUNK = {
    "celex": "32013R0952",
    "text": "Douaneautoriteit en invoerrechten.",
    "article_number": "1",
}


@pytest.mark.asyncio
async def test_invalid_evidence_blocks_answer_generation():
    service = AgentAnswerService()
    request = QueryRequest(
        question="Wanneer mag een toezichthouder een product van de markt halen?",
        audience="professional",
        language="nl",
    )
    plan = LegalInterpretationPlan(
        legal_actor="authority",
        legal_domain="administrative_law",
        legal_question_type="enforcement",
    )
    fetch = AgentFetchResult(chunks=[WEAK_CHUNK], fetch_attempted=True, attempted_celex=["32013R0952"])
    evidence = EvidenceValidationResult(is_valid=False, reasons=["domain_mismatch"])
    bundle = await service.build(request, fetch, plan, None, evidence)
    assert bundle["coverage_status"] == "insufficient"
    assert "onvoldoende betrouwbare EUR-Lex-bronnen" in bundle["answer_text"]
    assert "**Ja.**" not in bundle["answer_text"]

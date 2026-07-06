"""Declarant-workflow acceptance scenarios — iteration gate."""
from __future__ import annotations

import pytest

from backend.src.services.declarant_query_service import DeclarantQueryService
from backend.src.services.legal_hypothesis_service import LegalHypothesisService
from backend.src.services.primary_legal_conflict_service import select_primary_legal_conflict
from shared.schemas.query import QueryRequest

_FORBIDDEN = (
    "marktdeelnemers onder",
    "governance, transparantie, rapportage",
    "celex ,",
)

CLARIFY_META = {"coverage_status": "clarify_only", "verification_questions": ["contentwebsite"]}


def _forbidden_in(text: str) -> list[str]:
    lowered = text.lower()
    return [marker for marker in _FORBIDDEN if marker in lowered]


async def _two_turn(question: str, chip: str) -> tuple[object, str]:
    service = DeclarantQueryService()
    req1 = QueryRequest(question=question, audience="layperson", language="nl")
    r1, _, _, _ = await service.query(req1, history=[])
    history = [
        {"role": "user", "content": question},
        {"role": "assistant", "content": r1.answer or "", "metadata": {
            "coverage_status": r1.coverage_status,
            "verification_questions": r1.verification_questions,
        }},
    ]
    req2 = QueryRequest(question=chip, audience="layperson", language="nl")
    r2, _, chunks, _ = await service.query(req2, history=history)
    celexes = {str(c.get("celex", "")) for c in chunks}
    return r2, ",".join(sorted(celexes))


@pytest.mark.asyncio
async def test_i1_routing_not_consumer_rights():
    merged = "moet ik me in de eu kunnen legitimeren — verduidelijking: overheidsdienst / formulier"
    hyp = LegalHypothesisService()._rule_hypothesis(merged)
    conflict = select_primary_legal_conflict(merged, hyp)
    assert conflict == "identity_verification_issue"


@pytest.mark.asyncio
async def test_d1_platform_contentwebsite_not_consumer():
    r2, celexes = await _two_turn("mag ik een platform bouwen", "contentwebsite")
    answer = r2.answer or ""
    assert "32011L0083" not in celexes or "consumer rights" not in answer.lower()
    assert not _forbidden_in(answer)
    if r2.coverage_status == "adequate":
        assert "32022R2065" in celexes
        assert "de wet zegt" in answer.lower()
        assert "artikel" in answer.lower()


@pytest.mark.asyncio
async def test_i1_follow_up_no_synthetic_consumer_answer():
    r2, celexes = await _two_turn(
        "moet ik me in de eu kunnen legitimeren",
        "overheidsdienst / formulier",
    )
    answer = (r2.answer or "").lower()
    assert "consumer rights" not in answer or r2.coverage_status != "adequate"
    assert not _forbidden_in(answer)
    if r2.coverage_status == "adequate":
        assert "32014R0910" in celexes or "32004L0038" in celexes
        assert "ik kon geen volledig onderbouwd antwoord" not in answer
        assert "artikel" in answer or "article" in answer


@pytest.mark.asyncio
async def test_c1_customs_routing_not_consumer():
    question = (
        "Ik verkoop via webshop kleine pakketjes vanuit China naar NL onder 150 euro. "
        "Moet ik douaneaangifte doen?"
    )
    hyp = LegalHypothesisService()._rule_hypothesis(question)
    conflict = select_primary_legal_conflict(question, hyp)
    assert conflict == "customs_import_issue"
    service = DeclarantQueryService()
    r, _, chunks, _ = await service.query(
        QueryRequest(question=question, audience="layperson", language="nl"),
        history=[],
    )
    answer = r.answer or ""
    assert not _forbidden_in(answer)
    if r.coverage_status == "adequate":
        assert any(c.get("celex") in ("32013R0952", "32015R2446") for c in chunks)

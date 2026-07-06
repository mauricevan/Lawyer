"""40-case declarant acceptance gate — catalog + layperson questions."""
from __future__ import annotations

import pytest

from backend.src.services.agent_query_service import AgentQueryService
from backend.src.services.legal_hypothesis_service import LegalHypothesisService
from backend.src.services.primary_legal_conflict_service import select_primary_legal_conflict
from backend.tests.acceptance.declarant_assertions import assert_declarant_answer, forbidden_markers
from backend.tests.fixtures.declarant_catalog import CATALOG_SCENARIOS, LAYPERSON_QUESTIONS
from shared.schemas.query import QueryRequest


async def _query(question: str, history: list[dict] | None = None) -> tuple[str, str, set[str]]:
    agent = AgentQueryService()
    response, _, chunks, _ = await agent.query(
        QueryRequest(question=question, audience="layperson", language="nl"),
        history=history or [],
    )
    celexes = {str(c.get("celex", "")) for c in chunks if c.get("celex")}
    return response.answer or "", response.coverage_status or "", celexes


async def _two_turn(question: str, chip: str) -> tuple[str, str, set[str]]:
    agent = AgentQueryService()
    r1, _, _, _ = await agent.query(
        QueryRequest(question=question, audience="layperson", language="nl"), history=[],
    )
    history = [
        {"role": "user", "content": question},
        {"role": "assistant", "content": r1.answer or "", "metadata": {
            "coverage_status": r1.coverage_status,
        }},
    ]
    return await _query(chip, history)


@pytest.mark.asyncio
@pytest.mark.parametrize("scenario", CATALOG_SCENARIOS, ids=[s.scenario_id for s in CATALOG_SCENARIOS])
async def test_catalog_scenario(scenario) -> None:
    if scenario.chip:
        answer, status, celexes = await _two_turn(scenario.question, scenario.chip)
    else:
        answer, status, celexes = await _query(scenario.question)
    failures = assert_declarant_answer(
        scenario.scenario_id, answer, status, celexes, scenario.expectation,
    )
    if scenario.scenario_id == "C1-routing":
        hyp = LegalHypothesisService()._rule_hypothesis(scenario.question)
        assert select_primary_legal_conflict(scenario.question, hyp) == "customs_import_issue"
        return
    if scenario.scenario_id == "D1-routing":
        hyp = LegalHypothesisService()._rule_hypothesis(scenario.question)
        assert select_primary_legal_conflict(scenario.question, hyp) == "platform_governance_issue"
        return
    if scenario.scenario_id == "N3-gap":
        assert status != "adequate" or not forbidden_markers(answer)
        return
    if scenario.scenario_id == "I1-followup":
        q = "moet ik me in de eu kunnen legitimeren"
        a1, _, _ = await _query(q)
        history = [
            {"role": "user", "content": q},
            {"role": "assistant", "content": a1},
            {"role": "user", "content": "overheidsdienst / formulier"},
        ]
        a2, _, _ = await _query("overheidsdienst / formulier", history)
        history.append({"role": "assistant", "content": a2})
        history.append({"role": "user", "content": scenario.question})
        answer, status, celexes = await _query(scenario.question, history)
        failures = assert_declarant_answer(
            scenario.scenario_id, answer, status, celexes, scenario.expectation,
        )
    assert not failures, "\n".join(failures)


@pytest.mark.asyncio
@pytest.mark.parametrize("question,expectation", LAYPERSON_QUESTIONS, ids=[p[1].scenario_id for p in LAYPERSON_QUESTIONS])
async def test_layperson_question(question, expectation) -> None:
    answer, status, celexes = await _query(question)
    failures = assert_declarant_answer(
        expectation.scenario_id, answer, status, celexes, expectation,
    )
    assert not forbidden_markers(answer) or status != "adequate"
    if expectation.required_celex and status == "adequate":
        assert not failures, "\n".join(failures)

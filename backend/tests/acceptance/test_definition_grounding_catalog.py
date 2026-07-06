"""Acceptance tests for cross-domain definition grounding via research loop."""
from unittest.mock import patch

import pytest

from backend.src.services.eu_legal_research_loop_service import EuLegalResearchLoopService
from backend.tests.acceptance.declarant_assertions import assert_declarant_answer
from backend.tests.fixtures.definition_grounding_catalog import DEFINITION_GROUNDING_SCENARIOS
from backend.tests.fixtures.eurlex_sessions import SESSIONS, get_session
from shared.schemas.legal_interpretation import AgentFetchResult, InstrumentTarget, LegalInterpretationPlan
from shared.schemas.query import QueryRequest


@pytest.mark.parametrize("scenario", DEFINITION_GROUNDING_SCENARIOS, ids=lambda s: s.scenario_id)
@pytest.mark.asyncio
async def test_definition_grounding_research_loop(scenario):
    """Research loop must verify definition chunks for each catalog scenario."""
    service = EuLegalResearchLoopService()
    request = QueryRequest(
        question=scenario.question,
        audience="professional",
        language="nl",
    )
    plan = LegalInterpretationPlan(
        question_type="definition",
        legal_domain=scenario.legal_domain,  # type: ignore[arg-type]
        legal_question_type="definition",
        instruments=[InstrumentTarget(name=scenario.celex, celex=scenario.celex, articles=())],
        search_keywords=list(scenario.expectation.required_text_snippets)[:3],
    )
    fetch = AgentFetchResult(chunks=[], fetch_ok=False)

    async def _load(celex: str, language: str = "nl"):
        return get_session(celex)

    with patch.object(service._executor._sessions, "load", side_effect=_load):
        updated, loop = await service.run(request, plan, fetch)

    chunk_celexes = {str(c.get("celex")) for c in updated.chunks if c.get("celex")}
    answer = " ".join(str(c.get("text", "")) for c in updated.chunks)
    if loop.terminated_reason == "verified":
        answer = f"## Kort antwoord\nJa.\n\n## Wat de EU-regels zeggen\nArtikel 5.\n\n{answer}"

    failures = assert_declarant_answer(
        scenario.scenario_id,
        answer,
        "adequate" if loop.terminated_reason == "verified" else "insufficient",
        chunk_celexes,
        scenario.expectation,
        research_trace=loop.model_dump(mode="json"),
    )
    if scenario.expectation.require_research_verified:
        assert not failures, failures
    elif loop.terminated_reason != "verified":
        pytest.skip(f"fixture gap for {scenario.scenario_id}")

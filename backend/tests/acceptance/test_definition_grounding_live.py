"""Live integration smoke for definition grounding (opt-in)."""
import os

import pytest

from backend.src.services.eu_legal_research_loop_service import EuLegalResearchLoopService
from backend.tests.fixtures.definition_grounding_catalog import DEFINITION_GROUNDING_SCENARIOS
from shared.schemas.legal_interpretation import AgentFetchResult, InstrumentTarget, LegalInterpretationPlan
from shared.schemas.query import QueryRequest

pytestmark = pytest.mark.integration


@pytest.mark.skipif(
    os.environ.get("DEFINITION_GROUNDING_LIVE") != "1",
    reason="Set DEFINITION_GROUNDING_LIVE=1 for live EUR-Lex smoke",
)
@pytest.mark.parametrize(
    "scenario",
    [s for s in DEFINITION_GROUNDING_SCENARIOS if s.expectation.require_research_verified],
    ids=lambda s: s.scenario_id,
)
@pytest.mark.asyncio
async def test_live_definition_grounding(scenario):
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
    )
    _, loop = await service.run(request, plan, AgentFetchResult(chunks=[]))
    assert loop.terminated_reason == "verified", loop.model_dump()

"""Tests for LLM legal planner and rule fallback."""
import pytest

from backend.src.services.llm_legal_planner_service import LlmLegalPlannerService
from shared.schemas.legal_interpretation import LegalInterpretationPlan, InstrumentTarget


@pytest.mark.asyncio
async def test_rule_fallback_resolves_reach_oj_citation(monkeypatch):
    async def fail_llm(*_args, **_kwargs):
        raise ValueError("no llm")

    monkeypatch.setattr(
        "backend.src.services.llm_legal_planner_service.call_llm_json",
        fail_llm,
    )
    planner = LlmLegalPlannerService()
    question = (
        "Wanneer moet een stof worden geregistreerd volgens de REACH-verordening "
        "(Verordening (EG) nr. 1907/2006)?"
    )
    plan = await planner.interpret(question)
    assert plan.planner_source == "rule_fallback"
    assert plan.instruments
    assert plan.instruments[0].celex == "32006R1907"


@pytest.mark.asyncio
async def test_rule_fallback_merges_articles_for_oj_citation(monkeypatch):
    async def fail_llm(*_args, **_kwargs):
        raise ValueError("no llm")

    monkeypatch.setattr(
        "backend.src.services.llm_legal_planner_service.call_llm_json",
        fail_llm,
    )
    planner = LlmLegalPlannerService()
    question = (
        "Welke verplichtingen heeft een fabrikant wanneer een product een veiligheidsrisico "
        "blijkt te vormen volgens Verordening (EU) 2023/988?"
    )
    plan = await planner.interpret(question)
    assert plan.instruments
    assert plan.instruments[0].celex == "32023R0988"
    assert "9" in plan.instruments[0].articles


@pytest.mark.asyncio
async def test_national_law_quick_check(monkeypatch):
    planner = LlmLegalPlannerService()
    plan = await planner.interpret("Hoeveel vakantiedagen heb ik volgens Nederlandse wet?")
    assert plan.is_national_law is True
    assert plan.is_eu_law is False
    assert plan.instruments == []


@pytest.mark.asyncio
async def test_llm_plan_used_when_confident(monkeypatch):
    async def mock_llm(*_args, **_kwargs):
        return {
            "question_type": "obligation",
            "is_eu_law": True,
            "is_national_law": False,
            "instruments": [
                {"name": "REACH", "oj_citation": "1907/2006", "articles": ["6"], "confidence": 0.9},
            ],
            "search_keywords": ["registratie"],
            "confidence": 0.9,
            "reasoning_brief": "REACH registratie",
        }

    monkeypatch.setattr(
        "backend.src.services.llm_legal_planner_service.call_llm_json",
        mock_llm,
    )
    planner = LlmLegalPlannerService()
    plan = await planner.interpret("Wanneer registreren onder REACH?")
    assert plan.planner_source == "llm"
    assert plan.instruments[0].name == "REACH"
    assert plan.confidence >= 0.5

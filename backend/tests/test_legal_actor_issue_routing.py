"""Tests for actor/domain plan context."""
from backend.src.utils.legal_actor_issue_routing import apply_context_to_plan
from shared.schemas.legal_interpretation import InstrumentTarget, LegalInterpretationPlan

CE_QUESTION = "Mag een fabrikant een product zonder CE-markering op de markt brengen?"


def test_apply_context_sets_three_layers_without_changing_instruments():
    plan = LegalInterpretationPlan(
        instruments=[
            InstrumentTarget(name="surveillance", celex="32019R1020", articles=["16"], confidence=0.8),
        ],
    )
    adjusted = apply_context_to_plan(plan, CE_QUESTION)
    assert adjusted.legal_actor == "manufacturer"
    assert adjusted.legal_domain == "product_safety"
    assert adjusted.legal_question_type == "market_access"
    assert adjusted.instruments[0].celex == "32019R1020"

"""Tests for legal source planner (ADR-0009)."""
from backend.src.services.legal_source_planner_service import LegalSourcePlannerService

CUSTOMS_REFUND = (
    "Een Nederlandse importeur heeft machines uit Japan ingevoerd. Na de invoer blijkt "
    "dat de douanewaarde te hoog is vastgesteld doordat een korting niet was verwerkt. "
    "Kan de importeur terugbetaling van invoerrechten krijgen?"
)


def test_planner_maps_customs_refund_to_ucc_articles():
    plan = LegalSourcePlannerService().plan(CUSTOMS_REFUND)
    assert plan is not None
    assert plan.celex == "32013R0952"
    assert "116" in plan.articles


def test_planner_maps_refund_deadline_to_article_121():
    plan = LegalSourcePlannerService().plan(
        "Binnen welke termijn moet ik een verzoek tot terugbetaling indienen?"
    )
    assert plan is not None
    assert plan.plan_id == "ucc_refund_deadline"
    assert plan.articles[0] == "121"


def test_planner_returns_none_for_unrelated_question():
    plan = LegalSourcePlannerService().plan("Wat is het weer morgen in Amsterdam?")
    assert plan is None

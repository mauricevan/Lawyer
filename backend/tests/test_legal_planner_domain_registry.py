"""Tests for domain-level CELEX planner registry."""
from backend.src.services.legal_planner_domain_registry import match_domain_plan
from backend.src.services.legal_source_planner_service import LegalSourcePlannerService


def test_domain_planner_maps_gdpr_question():
    plan = LegalSourcePlannerService().plan("Mag mijn werkgever mijn persoonsgegevens verwerken?")
    assert plan is not None
    assert plan.celex == "32016R0679"
    assert plan.legal_domain == "privacy"


def test_domain_planner_maps_ai_act():
    plan = LegalSourcePlannerService().plan("Welke regels gelden voor high-risk AI bij sollicitaties?")
    assert plan is not None
    assert plan.celex == "32024R1689"
    assert plan.plan_id == "ai_act_obligations"


def test_explicit_plan_beats_domain_for_refund_termijn():
    plan = LegalSourcePlannerService().plan(
        "Binnen welke termijn moet ik terugbetaling van invoerrechten aanvragen?"
    )
    assert plan is not None
    assert plan.plan_id == "ucc_refund_deadline"
    assert "121" in plan.articles


def test_domain_registry_matches_whistleblower():
    domain = match_domain_plan("Wat verplicht de EU-whistleblower-richtlijn werkgevers?")
    assert domain is not None
    assert domain.celex == "32024L1385"

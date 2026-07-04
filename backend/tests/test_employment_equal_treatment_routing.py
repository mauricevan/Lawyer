"""Tests for employment equal-treatment routing via generic planner + discovery."""
from backend.src.services.celex_discovery_service import CelexDiscoveryService
from backend.src.services.legal_source_planner_service import LegalSourcePlannerService
from backend.src.utils.legal_question_interpretation import infer_legal_context

EMPLOYMENT_QUESTION = (
    "Een werknemer in de EU wordt ontslagen terwijl hij langdurig ziek is. "
    "Welke EU-regels zijn relevant voor de bescherming tegen discriminatie op "
    "grond van handicap of gezondheid, en welke rechten kan de werknemer "
    "hieraan ontlenen?"
)


def test_infer_employee_domain():
    actor, issue = infer_legal_context(EMPLOYMENT_QUESTION)
    assert actor == "employee"
    from backend.src.services.legal_question_classifier_service import classify_legal_question
    assert classify_legal_question(EMPLOYMENT_QUESTION).legal_domain == "employment_law"


def test_planner_selects_equal_treatment_via_explicit_plan():
    discovery = CelexDiscoveryService().discover_sync(EMPLOYMENT_QUESTION, limit=5)
    plan = LegalSourcePlannerService().plan(EMPLOYMENT_QUESTION, discovery)
    assert plan is not None
    assert plan.celex == "32000L0078"
    assert plan.plan_id == "equal_treatment_employment"


def test_discovery_does_not_favor_ehds_for_employment_question():
    hits = CelexDiscoveryService().discover_sync(EMPLOYMENT_QUESTION, limit=8)
    ehds = next((hit for hit in hits if hit.celex == "32023R2859"), None)
    assert ehds is None or ehds.score < 0.35

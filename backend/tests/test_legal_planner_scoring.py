"""Tests for best-match legal source planner scoring."""
from backend.src.services.legal_planner_scoring import pick_best_explicit_plan, score_explicit_plan
from backend.src.services.legal_source_planner_service import LegalSourcePlannerService, _load_explicit_plans


def test_withdrawal_beats_ucc_on_termijn_word():
    question = (
        "Hoe lang bedraagt de herroepingstermijn voor een overeenkomst op afstand "
        "volgens Richtlijn 2011/83/EU?"
    ).lower()
    plans = _load_explicit_plans()
    consumer = next(p for p in plans if p["id"] == "consumer_withdrawal")
    ucc = next(p for p in plans if p["id"] == "ucc_refund_deadline")
    assert score_explicit_plan(question, consumer) > score_explicit_plan(question, ucc)
    plan = LegalSourcePlannerService().plan(question)
    assert plan is not None
    assert plan.plan_id == "consumer_withdrawal"


def test_ucc_deadline_still_matches_customs_question():
    question = "Binnen welke termijn moet ik een verzoek tot terugbetaling indienen?"
    plan = LegalSourcePlannerService().plan(question)
    assert plan is not None
    assert plan.plan_id == "ucc_refund_deadline"


def test_pick_best_requires_min_score():
    assert pick_best_explicit_plan("wat is het weer", _load_explicit_plans()) is None

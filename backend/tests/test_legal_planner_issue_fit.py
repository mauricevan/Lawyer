"""Tests for issue_fit scoring in explicit legal plans."""
from backend.src.services.legal_planner_scoring import pick_best_explicit_plan

GPSR_PLAN = {
    "id": "gpsr_manufacturer_risk",
    "celex": "32023R0988",
    "issue_fit": ["market_access", "obligation", "enforcement"],
    "triggers_any": ["fabrikant", "productveiligheid"],
}
SURVEILLANCE_PLAN = {
    "id": "product_conformity_doc",
    "celex": "32019R1020",
    "issue_fit": ["enforcement", "obligation"],
    "triggers_any": ["harmonisatiewetgeving", "conformiteitsverklaring", "fabrikant"],
}
CE_QUESTION = (
    "mag een fabrikant een product zonder ce-markering op de markt brengen"
)


def test_market_access_question_prefers_access_fit_plan():
    best = pick_best_explicit_plan(
        CE_QUESTION,
        [SURVEILLANCE_PLAN, GPSR_PLAN],
        min_score=5,
        legal_issue="market_access",
    )
    assert best is not None
    assert best["id"] == "gpsr_manufacturer_risk"

"""Tests for generic actor/issue CELEX discovery ranking."""
from backend.src.services.celex_discovery_service import CelexCandidate
from backend.src.utils.celex_discovery_ranking import rank_discovery_by_legal_context


def test_employee_actor_boosts_employment_domain_celex():
    candidates = [
        CelexCandidate(celex="32016R0679", score=0.85, source="title_index", title="GDPR"),
        CelexCandidate(celex="32000L0078", score=0.55, source="hint", title="Gelijke behandeling"),
    ]
    question = "Welke rechten heeft een werknemer bij discriminatie op het werk?"
    ranked = rank_discovery_by_legal_context(candidates, question)
    assert ranked[0].celex == "32000L0078"


def test_unknown_actor_leaves_order_unchanged():
    candidates = [
        CelexCandidate(celex="32016R0679", score=0.9, source="title_index"),
        CelexCandidate(celex="32000L0078", score=0.5, source="hint"),
    ]
    ranked = rank_discovery_by_legal_context(
        candidates, "Wat regelt de GDPR over gegevens?"
    )
    assert ranked[0].celex == "32016R0679"

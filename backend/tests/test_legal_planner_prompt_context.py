"""Tests for planner prompt interpretation hints."""
from backend.src.utils.legal_planner_prompt_context import build_planner_interpretation_hints


def test_hints_include_three_layers():
    question = "Mag een fabrikant een product zonder CE-markering op de markt brengen?"
    hints = build_planner_interpretation_hints(question)
    assert "legal_actor: manufacturer" in hints
    assert "legal_domain: product_safety" in hints
    assert "legal_question_type: market_access" in hints

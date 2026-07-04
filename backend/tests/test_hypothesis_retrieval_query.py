"""Tests for V4 conflict-only retrieval query."""
from backend.src.utils.hypothesis_retrieval_query import (
    build_analysis_retrieval_query,
    build_conflict_retrieval_query,
)
from shared.schemas.legal_conflict import LegalCaseAnalysis


def test_retrieval_query_uses_conflict_not_question_text():
    query = build_conflict_retrieval_query(
        "internal_market_restriction",
        "internal_market",
    )
    assert "internal market restriction" in query
    assert "internal market" in query
    assert "lidstaat" not in query


def test_analysis_retrieval_query():
    analysis = LegalCaseAnalysis(
        case_summary="Lidstaat eist lokale vertegenwoordiger voor e-commerce.",
        primary_legal_conflict="internal_market_restriction",
        legal_domain="internal_market",
        likely_eu_frameworks=["Directive 2000/31/EC"],
        default_celex="32000L0031",
    )
    query = build_analysis_retrieval_query(analysis)
    assert query == "internal market restriction internal market"

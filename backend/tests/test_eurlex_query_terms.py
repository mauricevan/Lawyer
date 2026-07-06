"""Tests for generic EUR-Lex query term extraction."""
from backend.src.utils.eurlex_query_terms import build_query_terms


def test_build_query_terms_from_question():
    terms = build_query_terms(
        "Welke Europese lidstaten doen mee aan de douane-unie?",
        ("douane", "unie"),
    )
    assert "douane" in terms
    assert "unie" in terms
    assert "lidstaten" in terms
    assert "de" not in terms


def test_build_query_terms_gdpr_question():
    terms = build_query_terms("Wanneer mag ik persoonsgegevens verwerken volgens de AVG?")
    assert "persoonsgegevens" in terms
    assert "verwerken" in terms

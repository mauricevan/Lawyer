"""Tests for curated CELEX hint matching."""
from ingestion.src.data.legal_term_hints import match_celex_hints, match_primary_celex_hint


def test_match_primary_hint_for_dsa():
    assert match_primary_celex_hint("Wat regelt DSA?") == "32022R2065"


def test_match_primary_hint_for_data_act():
    assert match_primary_celex_hint("Wat regelt Data Act?") == "32023R2854"


def test_longest_hint_wins_for_compound_label():
    assert match_primary_celex_hint("Wat is het doel van DSA Structure?") == "32022R1926"


def test_match_celex_hints_includes_explicit_celex():
    hints = match_celex_hints("Leg uit wat 32024R1689 vereist")
    assert "32024R1689" in hints

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


def test_chatbot_question_hints_ai_act():
    assert match_primary_celex_hint(
        "Moet ik mijn chatbot registreren bij de overheid?"
    ) == "32024R1689"


def test_oj_citation_2658_resolves_to_celex():
    assert match_primary_celex_hint("Verordening (EEG) nr. 2658/87") == "31987R2658"


def test_nomenclature_hint_resolves_to_celex():
    assert match_primary_celex_hint("Wat is de gecombineerde nomenclatuur?") == "31987R2658"


def test_whistleblower_question_hints_celex():
    assert match_primary_celex_hint(
        "Wat verplicht de EU-whistleblower-richtlijn werkgevers?"
    ) == "32024L1385"


def test_cookie_hint_resolves_eprivacy():
    assert match_primary_celex_hint("Moet mijn website een cookiebanner tonen?") == "32002L0058"


def test_flight_hint_resolves_eu261():
    assert match_primary_celex_hint("Mijn vlucht had 5 uur vertraging") == "32004R0261"


def test_mica_hint_resolves():
    assert match_primary_celex_hint("Welke EU-regels gelden voor crypto en MiCA?") == "32023R1114"


def test_warranty_hint_resolves_consumer_rights():
    assert match_primary_celex_hint("Hoe lang garantie heb ik bij online kopen?") == "32011L0083"


def test_energy_label_hint_resolves():
    assert match_primary_celex_hint("Moet verhuurder energielabel geven?") == "32010L0031"

"""Tests for V3 3-layer legal question classifier."""
from backend.src.services.legal_question_classifier_service import classify_legal_question

Q1 = "Mag een fabrikant een product zonder CE-markering op de EU-markt brengen?"
Q2 = "Mag een werknemer ontslagen worden wegens langdurige ziekte?"
Q3 = "Mag een consument een online aankoop binnen 14 dagen retourneren?"
Q4 = "Wanneer mag een lidstaat nationale regels invoeren die afwijken van EU-productregels?"
Q5 = "Wanneer mag een toezichthouder een product van de markt halen?"


def test_v3_product_safety_ce():
    result = classify_legal_question(Q1)
    assert result.legal_actor == "manufacturer"
    assert result.legal_domain == "product_safety"
    assert result.legal_question_type == "market_access"


def test_v3_employment_rights():
    result = classify_legal_question(Q2)
    assert result.legal_actor == "employee"
    assert result.legal_domain == "employment_law"
    assert result.legal_question_type == "rights"


def test_v3_consumer_protection():
    result = classify_legal_question(Q3)
    assert result.legal_actor == "consumer"
    assert result.legal_domain == "consumer_protection"
    assert result.legal_question_type == "rights"


def test_v3_internal_market_override():
    result = classify_legal_question(Q4)
    assert result.legal_actor == "authority"
    assert result.legal_domain == "internal_market"
    assert result.legal_question_type == "national_measure"


def test_v3_administrative_enforcement():
    result = classify_legal_question(Q5)
    assert result.legal_actor == "authority"
    assert result.legal_domain == "administrative_law"
    assert result.legal_question_type == "enforcement"


def test_v3_no_dsa_on_online_consumer_question():
    result = classify_legal_question(
        "Mag een consument online data van een platform opvragen?"
    )
    assert result.legal_domain != "digital_services"

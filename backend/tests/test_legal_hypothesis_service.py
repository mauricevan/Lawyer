"""Tests for v3 legal hypothesis service."""
from backend.src.services.legal_hypothesis_service import LegalHypothesisService

MEDICAL_HIRE_Q = (
    "Kan een werkgever binnen de Europese Unie een sollicitant verplichten om medische "
    "gegevens te verstrekken voordat een arbeidsovereenkomst wordt gesloten?"
)


def test_pre_employment_medical_hypothesis_employment_domain():
    hypothesis = LegalHypothesisService()._rule_hypothesis(MEDICAL_HIRE_Q)
    assert hypothesis.legal_domain_guess == "employment_law"
    assert hypothesis.legal_actor == "employee"

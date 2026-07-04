"""Tests for V4 primary legal conflict selection."""
from backend.src.services.legal_hypothesis_service import LegalHypothesisService
from backend.src.services.primary_legal_conflict_service import select_primary_legal_conflict
from backend.src.utils.conflict_domain_mapping import map_conflict_to_domain

ECOMMERCE_Q = (
    "Mag een EU-lidstaat eisen dat alle e-commerce webshops die in zijn land verkopen "
    "verplicht een lokale vertegenwoordiger aanstellen, en welke EU-regels bepalen "
    "of zo'n eis is toegestaan?"
)
MEDICAL_HIRE_Q = (
    "Kan een werkgever binnen de Europese Unie een sollicitant verplichten om medische "
    "gegevens te verstrekken voordat een arbeidsovereenkomst wordt gesloten?"
)
DSA_Q = "Welke verplichtingen heeft een platform onder de Digital Services Act bij illegale content?"


def test_ecommerce_lidstaat_selects_internal_market_conflict():
    hypothesis = LegalHypothesisService()._rule_hypothesis(ECOMMERCE_Q)
    conflict = select_primary_legal_conflict(ECOMMERCE_Q, hypothesis)
    assert conflict == "internal_market_restriction"
    mapping = map_conflict_to_domain(conflict)
    assert mapping.domain == "internal_market"
    assert mapping.default_celex == "32000L0031"


def test_pre_employment_selects_employment_conflict():
    hypothesis = LegalHypothesisService()._rule_hypothesis(MEDICAL_HIRE_Q)
    conflict = select_primary_legal_conflict(MEDICAL_HIRE_Q, hypothesis)
    assert conflict == "employment_relationship_issue"
    assert map_conflict_to_domain(conflict).domain == "employment_law"


def test_dsa_question_selects_platform_governance():
    hypothesis = LegalHypothesisService()._rule_hypothesis(DSA_Q)
    conflict = select_primary_legal_conflict(DSA_Q, hypothesis)
    assert conflict == "platform_governance_issue"
    assert map_conflict_to_domain(conflict).default_celex == "32022R2065"

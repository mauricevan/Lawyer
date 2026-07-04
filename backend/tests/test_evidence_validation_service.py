"""Tests for evidence validation layer."""
from backend.src.services.evidence_validation_service import EvidenceValidationService
from backend.src.utils.evidence_chunk_filters import is_procedural_chunk
from shared.schemas.legal_interpretation import LegalInterpretationPlan

GPSR_CHUNK = {
    "celex": "32023R0988",
    "text": (
        "De fabrikant mag alleen veilige producten op de markt brengen. "
        "CE-markering is verplicht waar de harmonisatiewetgeving dat voorschrijft."
    ),
    "article_number": "5",
}
CUSTOMS_CHUNK = {
    "celex": "32013R0952",
    "text": "Douaneautoriteit en douaneregeling via informatie- en communicatiesysteem.",
    "article_number": "12",
}
PROCEDURAL_CHUNK = {
    "celex": "32000L0078",
    "text": "Deze richtlijn treedt in werking op de twintigste dag na publicatieblad.",
    "article_number": "18",
}
EMPLOYMENT_CHUNK = {
    "celex": "32000L0078",
    "text": (
        "Werknemers mogen niet worden gediscrimineerd op grond van gezondheidstoestand "
        "of handicap. Lidstaten zorgen voor gelijke behandeling in arbeid."
    ),
    "article_number": "2",
}


def test_procedural_chunk_detected():
    assert is_procedural_chunk(PROCEDURAL_CHUNK["text"])


def test_passes_with_substantive_domain_chunk():
    plan = LegalInterpretationPlan(
        legal_actor="manufacturer",
        legal_domain="product_safety",
        legal_question_type="market_access",
    )
    result = EvidenceValidationService().validate(
        "Mag een fabrikant een product zonder CE-markering op de markt brengen?",
        [GPSR_CHUNK],
        plan,
    )
    assert result.is_valid
    assert result.validated_chunks


def test_fails_on_domain_mismatch():
    plan = LegalInterpretationPlan(
        legal_actor="authority",
        legal_domain="administrative_law",
        legal_question_type="enforcement",
    )
    result = EvidenceValidationService().validate(
        "Wanneer mag een toezichthouder een product van de markt halen?",
        [CUSTOMS_CHUNK],
        plan,
    )
    assert not result.is_valid
    assert "domain_mismatch" in result.reasons


def test_fails_on_procedural_only():
    plan = LegalInterpretationPlan(
        legal_actor="employee",
        legal_domain="employment_law",
        legal_question_type="rights",
    )
    result = EvidenceValidationService().validate(
        "Mag een werknemer ontslagen worden wegens langdurige ziekte?",
        [PROCEDURAL_CHUNK],
        plan,
    )
    assert not result.is_valid
    assert "procedural_only" in result.reasons


def test_passes_employment_rights_chunk():
    plan = LegalInterpretationPlan(
        legal_actor="employee",
        legal_domain="employment_law",
        legal_question_type="rights",
    )
    result = EvidenceValidationService().validate(
        "Mag een werknemer ontslagen worden wegens langdurige ziekte?",
        [EMPLOYMENT_CHUNK],
        plan,
    )
    assert result.is_valid

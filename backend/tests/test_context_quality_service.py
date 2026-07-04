"""Tests for batch context quality before LLM."""
from backend.src.services.context_quality_service import ContextQualityService

NAV_CHUNK = {
    "text": "Skip to main content My EUR-Lex sign in register javascript: click here",
    "celex": "31987R2658",
}
LEGAL_CHUNK = {
    "text": (
        "0101 Paarden, ezels, muilezels en hetzelven, levend. "
        "0101 21 00 Fokdieren van zuiver ras. Andere paarden voor import."
    ) * 4,
    "celex": "31987R2658",
}


def test_rejects_navigation_chunks():
    result = ContextQualityService().assess([NAV_CHUNK])
    assert not result.is_usable
    assert result.reason == "all_navigation"


def test_accepts_legal_classification_chunks():
    result = ContextQualityService().assess([LEGAL_CHUNK])
    assert result.is_usable
    assert result.best_score > 0


def test_rejects_metadata_for_classification_question():
    horse = (
        "Als ik een paard van zuiver ras importeer onder goederen code 0101 - "
        "is de kans dan groot dat deze goederencode juist is?"
    )
    metadata = {
        "text": (
            "CELEX:31987R2658 Publicatieblad Nr. L 256 Bijzondere uitgave EUR-Lex - "
            "Avis juridique important pour le document."
        ),
        "celex": "31987R2658",
        "score": 1.0,
    }
    result = ContextQualityService().assess([metadata], horse)
    assert not result.is_usable
    assert result.reason == "classification_context_gap"

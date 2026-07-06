"""Tests for layperson-friendly ILCL answer formatting."""
from backend.src.services.legal_clarification_orchestrator import LegalClarificationOrchestrator
from backend.src.utils.clarification_formatter import (
    format_clarification_section,
    verification_questions_from_result,
)
from shared.schemas.legal_clarification import ClarificationQuestion, LegalClarificationResult


def test_layperson_questions_mode_has_no_numbered_duplicate_list():
    result = LegalClarificationResult(
        state="ambiguous",
        mode="questions",
        questions=[
            ClarificationQuestion(
                id="platform_type",
                prompt="Wat voor platform bedoel u?",
                options=["marktplaats", "social media"],
            ),
        ],
        should_proceed=False,
    )
    section = format_clarification_section(result, audience="layperson")
    assert "1." not in section
    assert "marktplaats" not in section
    assert "Kies wat het best past" in section


def test_professional_questions_mode_keeps_detailed_list():
    result = LegalClarificationResult(
        state="ambiguous",
        mode="questions",
        questions=[
            ClarificationQuestion(
                id="platform_type",
                prompt="Wat voor platform bedoel u?",
                options=["marktplaats"],
            ),
        ],
        should_proceed=False,
    )
    section = format_clarification_section(result, audience="professional")
    assert "1. Wat voor platform bedoel u?" in section
    assert "marktplaats" in section


def test_vague_platform_question_still_exposes_clickable_chips():
    result = LegalClarificationOrchestrator().clarify("Mag ik een platform starten?")
    chips = verification_questions_from_result(result)
    assert "marktplaats" in chips

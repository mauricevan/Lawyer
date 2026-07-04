"""Tests for insufficient coverage layperson copy."""
from backend.src.services.coverage_guidance_service import CoverageGuidanceService
from backend.src.services.insufficient_coverage_answer_service import InsufficientCoverageAnswerService


def test_layperson_gap_does_not_use_old_boilerplate():
    guidance = CoverageGuidanceService().resolve("Wat is het minimumloon in Nederland?")
    answer = InsufficientCoverageAnswerService().build(
        guidance, "topic_not_in_corpus", "layperson",
    )
    assert "buiten wat ik nu betrouwbaar" not in answer.lower()
    assert "## Kort antwoord" in answer
    assert "## Wat u wél kunt doen" in answer


def test_layperson_gap_has_next_steps():
    guidance = CoverageGuidanceService().resolve("Wat is het minimumloon in Nederland?")
    answer = InsufficientCoverageAnswerService().build(
        guidance, "topic_not_in_corpus", "layperson",
    )
    assert "Juridisch Loket" in answer or "EUR-Lex" in answer

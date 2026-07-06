"""Tests for conversation-first layperson clarification guidance."""
from backend.src.services.legal_clarification_orchestrator import LegalClarificationOrchestrator
from backend.src.services.layperson_clarification_guide_service import LaypersonClarificationGuideService
from backend.src.utils.clarification_formatter import format_clarification_section
from backend.src.utils.layperson_clarification_copy import format_layperson_clarification_intro


def test_vague_platform_never_gets_generic_situation_chips():
    result = LegalClarificationOrchestrator().clarify("Mag ik een platform starten?", audience="layperson")
    from backend.src.utils.clarification_formatter import verification_questions_from_result

    chips = verification_questions_from_result(result)
    assert "reizen" not in chips
    assert "winkel of dienst" not in chips
    assert "marktplaats" in chips


def test_layperson_intro_mirrors_user_question():
    result = LegalClarificationOrchestrator().clarify("Mag ik een platform starten?", audience="layperson")
    assert "**Uw vraag:**" in result.formatted_section
    assert "platform starten" in result.formatted_section.lower()
    assert result.questions[0].prompt


def test_guide_returns_single_contextual_question_for_data():
    question = LaypersonClarificationGuideService().build(
        "Mag ik data van klanten opslaan?",
        ["geen actor", "geen geografische context"],
    )
    assert "gegevens" in question.prompt.lower() or "data" in question.prompt.lower()
    assert "reizen" not in question.options


def test_format_intro_is_conversational():
    text = format_layperson_clarification_intro(
        "Mag ik een platform starten?",
        "Wat voor platform bedoelt u?",
        "online platformen",
    )
    assert "Uw vraag:" in text
    assert "Wat voor platform bedoelt u?" in text

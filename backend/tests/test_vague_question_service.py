"""Tests for vague question detection."""
from backend.src.services.vague_question_service import VagueQuestionService


def test_mag_ik_dit_is_vague() -> None:
    service = VagueQuestionService()
    assert service.is_vague("Mag ik dit?")


def test_chatbot_question_is_not_vague() -> None:
    service = VagueQuestionService()
    question = "Moet ik mijn chatbot registreren bij de overheid?"
    assert not service.is_vague(question)


def test_build_questions_for_layperson() -> None:
    service = VagueQuestionService()
    questions = service.build_questions("layperson")
    assert len(questions) >= 2

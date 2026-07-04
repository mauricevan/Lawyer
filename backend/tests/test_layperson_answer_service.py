"""Tests for layperson answer service."""
from backend.src.services.layperson_answer_service import LaypersonAnswerService

GOOD_ANSWER = (
    "## Kort antwoord\n"
    "U hebt onder de AVG recht op gegevensoverdraagbaarheid van uw playlists.\n\n"
    "## Uitleg\n"
    "De AVG verplicht diensten om uw gegevens in een overdraagbaar formaat te geven "
    "wanneer u dat vraagt en de verwerking op toestemming of contract is gebaseerd."
)


def test_format_adds_sections_for_plain_text():
    service = LaypersonAnswerService()
    result = service.format("Korte uitleg zonder koppen.", "Spotify playlists", [])
    assert "## Kort antwoord" in result
    assert "## Wat betekent dit in de praktijk?" in result


def test_is_weak_flags_short_answers():
    service = LaypersonAnswerService()
    assert service.is_weak("Te kort.")
    assert not service.is_weak(GOOD_ANSWER)


def test_format_strips_celex_from_llm_output():
    service = LaypersonAnswerService()
    raw = GOOD_ANSWER + "\n\nCELEX:32016R0679"
    result = service.format(raw, "Spotify", [{"text": "gegevensoverdraagbaarheid", "title": "AVG"}])
    assert "32016R0679" not in result

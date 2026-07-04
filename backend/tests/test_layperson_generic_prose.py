"""Tests for domain-agnostic layperson prose builders."""
from backend.src.services.layperson_obligation_fallback_service import LaypersonObligationFallbackService
from backend.src.utils.layperson_generic_prose import build_kort_antwoord, build_voorbeeld
from shared.schemas.layperson_clear_answer import ObligationRow

EMPLOYMENT_QUESTION = (
    "Een werknemer in de EU wordt ontslagen terwijl hij langdurig ziek is. "
    "Welke EU-regels zijn relevant voor de bescherming tegen discriminatie op "
    "grond van handicap of gezondheid, en welke rechten kan de werknemer "
    "hieraan ontlenen?"
)
OBLIGATIONS = [
    ObligationRow(label="Geen discriminatie", uitleg="Verboden op grond van gezondheid."),
    ObligationRow(label="Bewijslast", uitleg="Werkgever moet aantonen dat geen discriminatie speelde."),
]


def test_kort_antwoord_uses_question_polarity_not_plan_id():
    kort = build_kort_antwoord(EMPLOYMENT_QUESTION, "Richtlijn 2000/78/EG", OBLIGATIONS)
    assert "**Ja.**" not in kort
    assert "2000/78" in kort
    assert "stelt onder meer deze verplichtingen" not in kort


def test_voorbeeld_generated_for_any_actor():
    example = build_voorbeeld(EMPLOYMENT_QUESTION, OBLIGATIONS)
    assert "werknemer" in example.lower()
    assert len(example) > 80


def test_obligation_fallback_without_chunks_is_complete():
    answer = LaypersonObligationFallbackService().compose(EMPLOYMENT_QUESTION, [])
    assert answer
    assert answer.count("## Kort antwoord") == 1
    assert "## Voorbeeld" in answer
    assert "## Juridische basis" in answer
    assert "| Geen discriminatie |" in answer

"""Tests for V10.3 Interactive Legal Clarification Layer."""
from backend.src.services.legal_ambiguity_detector_service import LegalAmbiguityDetectorService
from backend.src.services.legal_clarification_gate_service import LegalClarificationGateService
from backend.src.services.legal_clarification_orchestrator import LegalClarificationOrchestrator
from shared.schemas.query import QueryRequest

PLATFORM_DETAIL_Q = (
    "Ik wil een klein online platform starten waar consumenten onderling spullen verkopen, "
    "maar ook enkele bedrijven mogen adverteren. Moet ik daarvoor vooraf toestemming "
    "vragen in de EU en welke regels zijn het belangrijkst?"
)
VAGUE_PLATFORM_Q = "Mag ik een platform starten?"
IDENTIFICATION_Q = (
    "Wat voor soort legitimatie heb ik in de EU nodig om mij zelf te legitimeren?"
)
DATA_STORAGE_Q = (
    "wat zegt de eu wetgeving over het opslaan van data van derden"
)
VAGUE_DATA_Q = "Hoe zit het met privacy voor mijn bedrijf?"
NON_EU_Q = "Welke Amerikaanse wet geldt voor mijn app in California?"


def test_detailed_platform_question_is_clear():
    state, score, _ = LegalAmbiguityDetectorService().detect(PLATFORM_DETAIL_Q)
    assert state == "clear"
    assert score < 0.35


def test_vague_platform_question_triggers_clarification_questions():
    result = LegalClarificationOrchestrator().clarify(VAGUE_PLATFORM_Q)
    assert result.state == "ambiguous"
    assert result.mode == "questions"
    assert result.should_proceed is False
    assert result.questions
    assert "juridisch pas precies" in result.formatted_section.lower() or "uw vraag:" in result.formatted_section.lower()
    from backend.src.utils.clarification_formatter import verification_questions_from_result
    chips = verification_questions_from_result(result)
    assert "marktplaats" in chips


def test_identification_question_gets_relevant_chips_or_proceeds():
    result = LegalClarificationOrchestrator().clarify(IDENTIFICATION_Q, audience="layperson")
    from backend.src.utils.clarification_formatter import verification_questions_from_result

    if result.mode == "skip":
        assert result.should_proceed is True
        return
    chips = verification_questions_from_result(result)
    assert result.mode == "questions"
    assert "marktplaats" not in chips
    assert "online account / app" in chips or "bank of betaling" in chips


def test_data_storage_eu_question_proceeds_without_dumb_chips():
    state, score, _ = LegalAmbiguityDetectorService().detect(DATA_STORAGE_Q)
    assert state == "clear"
    result = LegalClarificationOrchestrator().clarify(DATA_STORAGE_Q, audience="layperson")
    assert result.should_proceed is True
    assert result.mode == "skip"


def test_vague_data_question_gets_relevant_storage_chips():
    result = LegalClarificationOrchestrator().clarify(VAGUE_DATA_Q, audience="layperson")
    from backend.src.utils.clarification_formatter import verification_questions_from_result

    chips = verification_questions_from_result(result)
    assert result.mode == "questions"
    assert "reizen" not in chips
    assert "winkel of dienst" not in chips
    assert any("bedrijf" in chip.lower() or "gegevens" in chip.lower() for chip in chips)


def test_concrete_data_storage_question_proceeds_without_chips():
    result = LegalClarificationOrchestrator().clarify(
        "Mag ik data van klanten opslaan?", audience="layperson",
    )
    assert result.should_proceed is True
    assert result.mode == "skip"


def test_non_eu_question_is_unanswerable():
    result = LegalClarificationOrchestrator().clarify(NON_EU_Q)
    assert result.state == "unanswerable"
    assert result.should_proceed is False


def test_assumption_mode_enriches_question_for_follow_up_refusal():
    history = [
        {"role": "user", "content": VAGUE_PLATFORM_Q},
        {
            "role": "assistant",
            "content": "Ik kan dit juridisch pas precies beoordelen als ik meer weet.",
        },
    ]
    result = LegalClarificationOrchestrator().clarify("Weet ik niet, kies maar", history=history)
    assert result.mode == "assumption"
    assert result.should_proceed is True
    assert "ILCL-aanname" in result.enriched_question


def test_second_turn_with_detail_proceeds_clear():
    history = [
        {"role": "user", "content": VAGUE_PLATFORM_Q},
        {
            "role": "assistant",
            "content": "Ik kan dit juridisch pas precies beoordelen als ik meer weet.",
        },
    ]
    follow_up = (
        "Een marktplaats waar particulieren spullen verkopen. "
        "Ik ben ondernemer en richt me op de EU."
    )
    result = LegalClarificationOrchestrator().clarify(follow_up, history=history)
    assert result.state == "clear"
    assert result.should_proceed is True


def test_single_chip_answer_after_layperson_clarification_proceeds():
    history = [
        {"role": "user", "content": VAGUE_PLATFORM_Q},
        {
            "role": "assistant",
            "content": (
                "Om u een concreet antwoord te geven, mis ik nog wat context over uw situatie. "
                "Klik hieronder op wat het best past."
            ),
        },
    ]
    result = LegalClarificationOrchestrator().clarify("marktplaats", history=history, audience="layperson")
    assert result.mode == "assumption"
    assert result.should_proceed is True
    assert "marktplaats" in result.enriched_question.lower()


def test_scenario_selection_proceeds_with_assumption():
    history = [
        {"role": "user", "content": VAGUE_PLATFORM_Q},
        {
            "role": "assistant",
            "content": "Uw vraag kan op meerdere manieren worden begrepen. Klik op een optie hieronder.",
        },
    ]
    result = LegalClarificationOrchestrator().clarify("A. Online marktplaats starten", history=history)
    assert result.mode == "assumption"
    assert result.should_proceed is True
    assert "ILCL-scenario A" in result.enriched_question


def test_second_turn_without_refusal_offers_scenarios():
    history = [
        {"role": "user", "content": VAGUE_PLATFORM_Q},
        {
            "role": "assistant",
            "content": "Om u een concreet antwoord te geven, mis ik nog wat context over uw situatie.",
        },
    ]
    result = LegalClarificationOrchestrator().clarify("Hmm, nog niet zeker", history=history)
    assert result.mode == "scenarios"
    assert result.should_proceed is False
    assert len(result.scenarios) >= 2


def test_chip_answer_skips_vague_gate_after_clarification():
    """Short chip labels must reach ILCL after a clarification turn, not the vague gate."""
    from backend.src.services.vague_question_service import VagueQuestionService
    from backend.src.utils.clarification_history_merge import prior_clarification_turn

    history = [
        {"role": "user", "content": VAGUE_PLATFORM_Q},
        {
            "role": "assistant",
            "content": "Om u een concreet antwoord te geven, mis ik nog wat context over uw situatie.",
        },
    ]
    vague = VagueQuestionService()
    assert vague.is_vague("marktplaats")
    assert prior_clarification_turn(history)
    assert not (not prior_clarification_turn(history) and vague.is_vague("marktplaats"))


def test_ilcl_gate_blocks_retrieval_for_vague_question():
    request = QueryRequest(question=VAGUE_PLATFORM_Q, audience="layperson")
    _, result, bundle = LegalClarificationGateService().gate(request)
    assert bundle is not None
    assert bundle["coverage_status"] == "clarify_only"
    assert result is not None
    assert result.mode == "questions"


def test_ilcl_gate_proceeds_for_clear_platform_question():
    request = QueryRequest(question=PLATFORM_DETAIL_Q, audience="layperson")
    enriched, result, bundle = LegalClarificationGateService().gate(request)
    assert bundle is None
    assert enriched.question == PLATFORM_DETAIL_Q


def test_definition_lookup_proceeds_without_clarification() -> None:
    for question in (
        "Wat is een persoonsgegeven volgens de AVG?",
        "Wat betekent fabrikant in de GPSR?",
    ):
        result = LegalClarificationOrchestrator().clarify(question, audience="layperson")
        assert result.should_proceed is True
        assert result.state == "clear"

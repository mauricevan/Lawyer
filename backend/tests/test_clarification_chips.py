"""Tests for ILCL chip filtering and clarification history merge."""
from backend.src.utils.clarification_chip_filter import filter_layperson_chips, is_valid_layperson_chip
from backend.src.utils.clarification_formatter import format_clarification_section, verification_questions_from_result
from backend.src.utils.clarification_history_merge import (
    merge_clarification_history,
    prior_clarification_turn,
)
from backend.src.services.legal_clarification_orchestrator import LegalClarificationOrchestrator
from backend.src.utils.question_typo_normalizer import normalize_question_typos
from shared.schemas.legal_clarification import ClarificationQuestion, LegalClarificationResult


LAYPERSON_CLARIFY_CONTENT = (
    "**Uw vraag:** Mag ik een platform beginnen?\n\n"
    "Dit soort vragen gaat meestal over **online platformen en digitale diensten (o.a. DSA)**.\n\n"
    "**Wat voor platform of online dienst bedoelt u?**\n\n"
    "Kies wat het best past — of typ het antwoord in het veld hieronder."
)


def test_prior_clarification_detects_layperson_formatted_content():
    history = [
        {"role": "user", "content": "Mag ik een platform beginnen?"},
        {"role": "assistant", "content": LAYPERSON_CLARIFY_CONTENT},
    ]
    assert prior_clarification_turn(history) is True


def test_prior_clarification_detects_metadata_clarify_only():
    history = [
        {"role": "user", "content": "Mag ik een platform beginnen?"},
        {
            "role": "assistant",
            "content": "kort",
            "metadata": {
                "coverage_status": "clarify_only",
                "verification_questions": ["marktplaats", "social media"],
            },
        },
    ]
    assert prior_clarification_turn(history) is True


def test_chip_click_merges_and_proceeds_after_layperson_clarification():
    history = [
        {"role": "user", "content": "Mag ik een platform beginnen?"},
        {"role": "assistant", "content": LAYPERSON_CLARIFY_CONTENT},
    ]
    merged = merge_clarification_history("marktplaats", history)
    assert "platform beginnen" in merged.lower()
    assert "marktplaats" in merged.lower()
    result = LegalClarificationOrchestrator().clarify("marktplaats", history=history, audience="layperson")
    assert result.should_proceed is True
    assert result.mode == "assumption"


def test_typo_platfrom_gets_platform_chips():
    result = LegalClarificationOrchestrator().clarify(
        "mag ik een platfrom beginnen",
        audience="layperson",
    )
    chips = verification_questions_from_result(result, "layperson")
    assert "marktplaats" in chips
    assert "reizen" not in chips


def test_invalid_question_chips_are_filtered():
    assert not is_valid_layperson_chip("Waar gaat uw vraag precies over (bijv. privacy, AI, arbeid)?")
    assert not is_valid_layperson_chip("In welk land woont of werkt u?")
    assert is_valid_layperson_chip("online account / app")
    filtered = filter_layperson_chips([
        "marktplaats",
        "Waar gaat uw vraag precies over (bijv. privacy, AI, arbeid)?",
        "social media",
    ])
    assert filtered == ["marktplaats", "social media"]


def test_identification_question_has_context_chips_not_country():
    result = LegalClarificationOrchestrator().clarify(
        "Wat voor legitimatie heb ik in de EU nodig?",
        audience="layperson",
    )
    chips = verification_questions_from_result(result, "layperson")
    if result.mode == "skip":
        assert result.should_proceed is True
        return
    assert chips
    assert not any("land" in chip.lower() for chip in chips)
    assert any("account" in chip.lower() or "bank" in chip.lower() for chip in chips)


def test_normalize_platfrom_typo():
    assert "platform" in normalize_question_typos("mag ik een platfrom beginnen")

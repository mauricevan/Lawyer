"""Tests for clear short operational questions in ILCL."""
from backend.src.services.legal_ambiguity_detector_service import LegalAmbiguityDetectorService


def test_data_storage_question_is_clear_without_chip():
    state, score, _ = LegalAmbiguityDetectorService().detect(
        "Mag ik data van klanten opslaan?",
    )
    assert state == "clear"
    assert score < 0.35


def test_customs_declaration_question_is_clear():
    state, _, _ = LegalAmbiguityDetectorService().detect("Moet ik douaneaangifte doen?")
    assert state == "clear"


def test_customs_union_member_list_is_clear():
    state, score, _ = LegalAmbiguityDetectorService().detect(
        "welke europese lidstaten doen mee aan de douane unie",
    )
    assert state == "clear"
    assert score < 0.35

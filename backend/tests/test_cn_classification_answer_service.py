"""Tests for deterministic CN classification answers."""
from backend.src.services.cn_classification_answer_service import CnClassificationAnswerService
from backend.src.services.cn_classification_service import CnClassificationService

HORSE_QUESTION = (
    "Als ik een paard van zuiver ras importeer onder goederen code 0101 - "
    "is de kans dan groot dat deze goederencode juist is?"
)


def test_cn_service_resolves_horse_position() -> None:
    match = CnClassificationService().resolve(HORSE_QUESTION)
    assert match is not None
    assert match.position_code == "0101"
    assert match.subheading is not None
    assert match.subheading.code == "0101 21 00"


def test_cn_answer_includes_disclaimer_and_subheading() -> None:
    match = CnClassificationService().resolve(HORSE_QUESTION)
    assert match is not None
    answer = CnClassificationAnswerService().build(match, audience="layperson")
    assert "0101 21 00" in answer
    assert "bindende douane-classificatie" in answer
    assert "TARIC" in answer

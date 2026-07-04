"""Tests for CN/TARIC code detection in user questions."""
from ingestion.src.data.cn_code_parser import (
    extract_cn_code,
    extract_cn_code_full,
    is_classification_question,
)

HORSE_QUESTION = (
    "Als ik een paard van zuiver ras importeer onder goederen code 0101 - "
    "is de kans dan groot dat deze goederencode juist is?"
)


def test_extract_cn_code_returns_position() -> None:
    assert extract_cn_code(HORSE_QUESTION) == "0101"


def test_extract_cn_code_full_with_subheading() -> None:
    assert extract_cn_code_full("goederencode 0101 21 00 voor fokpaard") == "01012100"


def test_is_classification_question_for_horse_import() -> None:
    assert is_classification_question(HORSE_QUESTION)


def test_is_classification_question_requires_code() -> None:
    assert not is_classification_question("Mag ik een paard importeren?")

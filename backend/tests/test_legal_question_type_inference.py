"""Tests for V3 legal question type inference."""
from backend.src.utils.legal_question_type_inference import infer_legal_question_type


def test_national_measure_for_lidstaat():
    qtype = infer_legal_question_type(
        "Wanneer mag een lidstaat nationale regels invoeren?",
        "authority",
        "internal_market",
    )
    assert qtype == "national_measure"

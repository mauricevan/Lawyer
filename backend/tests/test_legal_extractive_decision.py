"""Tests for extractive answer decision logic."""
from backend.src.services.legal_extractive_decision import should_use_extractive_answer

CHUNKS = [{
    "celex": "32016R0679",
    "article_number": "6",
    "title": "AVG",
    "text": (
        "Artikel 6 Rechtmatigheid van de verwerking 1. De verwerking is slechts rechtmatig "
        "indien en voor zover aan minstens één van de grondslagen van lid 1 is voldaan."
    ) * 2,
}]


def test_prefers_extractive_when_llm_answer_has_xml():
    weak = "Op basis van L_2013269NL.01000101.xml artikel 6 verwerking persoonsgegevens."
    assert should_use_extractive_answer(weak, CHUNKS, "professional", "AVG verwerking")


def test_prefers_extractive_when_missing_kort_antwoord():
    assert should_use_extractive_answer("Algemene uitleg zonder structuur.", CHUNKS, "layperson")


def test_skips_extractive_without_usable_chunks():
    assert not should_use_extractive_answer("", [{"text": "kort", "celex": "32016R0679"}], "layperson")

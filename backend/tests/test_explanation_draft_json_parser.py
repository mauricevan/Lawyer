"""Tests for JSON section parsing into ExplanationSections."""
from backend.src.utils.explanation_draft_json_parser import parse_sections_json


def test_parses_json_object_with_section_keys() -> None:
    raw = (
        '{"short_answer": "Ja, onder voorwaarden.", "law_says": "Artikel 5.", '
        '"practical_meaning": "Transparantie.", "legal_sources": "DSA", '
        '"uncertainties": "Geen.", "disclaimer": "Geen advies."}'
    )
    sections = parse_sections_json(raw)
    assert sections is not None
    assert "voorwaarden" in sections.short_answer
    assert sections.law_says == "Artikel 5."


def test_parses_fenced_json_block() -> None:
    raw = '```json\n{"short_answer": "Hello", "law_says": "Law"}\n```'
    sections = parse_sections_json(raw)
    assert sections is not None
    assert sections.short_answer == "Hello"


def test_returns_none_for_markdown() -> None:
    assert parse_sections_json("## Kort antwoord\nHello") is None

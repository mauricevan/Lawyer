"""Tests for markdown ↔ semantic section mapping."""
from backend.src.utils.explanation_section_mapper import markdown_to_sections, sections_to_markdown


def test_maps_kort_antwoord_and_juridische_basis() -> None:
    text = (
        "## Kort antwoord\nDirect antwoord.\n\n"
        "## Juridische basis\nArtikel 5 regelt X.\n\n"
        "## Wat betekent dit in de praktijk?\n| A | B |"
    )
    sections = markdown_to_sections(text, "Footer disclaimer")
    assert "Direct antwoord" in sections.short_answer
    assert "Artikel 5" in sections.law_says
    assert "| A | B |" in sections.practical_meaning


def test_roundtrip_preserves_core_content() -> None:
    original = markdown_to_sections(
        "## Kort antwoord\nHello\n\n## Juridische basis\nLaw text",
        "Disc",
    )
    rendered = sections_to_markdown(original)
    reparsed = markdown_to_sections(rendered, "Disc")
    assert "Hello" in reparsed.short_answer
    assert "Law text" in reparsed.law_says

"""Tests for layperson LLM synthesis service."""
from backend.src.services.layperson_synthesis_service import LaypersonSynthesisService

SAMPLE_RAW = {
    "kort_antwoord": "Ja. Exploitanten moeten milieuschade voorkomen en herstellen.",
    "obligations": [
        {"label": "Melden", "uitleg": "Informeer de autoriteit bij schade."},
        {"label": "Herstellen", "uitleg": "Herstel de milieuschade."},
        {"label": "Voorkomen", "uitleg": "Neem preventieve maatregelen."},
    ],
    "voorbeeld": "Een bedrijf lekt stoffen in een rivier.",
    "juridische_basis": [
        {"article": "5", "title": "Preventie", "uitleg_nl": "Neem maatregelen bij dreigende schade."},
    ],
    "begrippen": [{"term": "exploitant", "definition_nl": "De verantwoordelijke onderneming."}],
    "let_op": "Lidstaten stellen de uitvoering vast.",
}

CHUNK = {
    "celex": "32004L0035",
    "article_number": "5",
    "text": "De exploitant neemt de nodige preventieve maatregelen wanneer milieuschade dreigt.",
}


def test_parse_synthesis_builds_clear_answer():
    service = LaypersonSynthesisService()
    answer = service.build_from_dict(SAMPLE_RAW, [CHUNK])
    assert answer.kort_antwoord.startswith("Ja.")
    assert len(answer.obligations) == 3
    assert answer.official_excerpts


def test_build_from_dict_renders_markdown_sections():
    from backend.src.utils.layperson_clear_markdown import render_clear_answer

    service = LaypersonSynthesisService()
    answer = service.build_from_dict(SAMPLE_RAW, [CHUNK])
    md = render_clear_answer(answer)
    assert "## Wat betekent dit in de praktijk?" in md
    assert "## Voorbeeld" in md
    assert "## Juridische basis" in md

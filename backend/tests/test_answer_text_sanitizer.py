"""Tests for answer text sanitization."""
from backend.src.utils.answer_text_sanitizer import sanitize_answer_text


def test_layperson_removes_artikel_none() -> None:
    raw = "Volgens artikel None moet u mogelijk registreren."
    cleaned = sanitize_answer_text(raw, "layperson")
    assert "none" not in cleaned.lower()
    assert "registreren" in cleaned.lower()


def test_professional_replaces_artikel_none() -> None:
    raw = "Zie Art. None in de AI Act."
    cleaned = sanitize_answer_text(raw, "professional")
    assert "Art. (onbekend)" in cleaned
    assert "None" not in cleaned


def test_layperson_replaces_weak_article_phrase() -> None:
    raw = "Op basis van GN lijkt artikel (onbekend) relevant voor uw vraag."
    cleaned = sanitize_answer_text(raw, "layperson")
    assert "onbekend" not in cleaned.lower()
    assert "de regels hier" in cleaned.lower()


def test_layperson_preserves_markdown_section_breaks() -> None:
    raw = "## Kort antwoord\nDit is het antwoord.\n\n## Uitleg\nMeer uitleg hier."
    cleaned = sanitize_answer_text(raw, "layperson")
    assert "## Kort antwoord" in cleaned
    assert "## Uitleg" in cleaned
    assert "\n\n" in cleaned
    assert "samenvatting hierboven" not in cleaned.lower()

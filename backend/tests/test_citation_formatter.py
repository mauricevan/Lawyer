"""Unit tests for CitationFormatter."""
import pytest

from backend.src.services.citation_formatter import CitationFormatter
from shared.schemas.citation import Citation, TrustIndicator


@pytest.fixture
def ai_act_citation() -> Citation:
    return Citation(
        celex="32024R1689",
        article="5",
        title="AI Act",
        excerpt="Verboden AI-praktijken...",
        eurlex_url="https://eur-lex.europa.eu/legal-content/NL/TXT/?uri=CELEX:32024R1689",
        trust=TrustIndicator(
            is_consolidated=True,
            is_in_force=True,
            oj_reference="L 2024/1689",
        ),
    )


def test_to_legal_format_ai_act(ai_act_citation: Citation) -> None:
    formatter = CitationFormatter()
    result = formatter.to_legal_format(ai_act_citation)
    assert "Artikel 5" in result
    assert "AI Act" in result
    assert "PbEU L 2024/1689" in result


def test_to_clipboard_includes_url(ai_act_citation: Citation) -> None:
    formatter = CitationFormatter()
    result = formatter.to_clipboard(ai_act_citation)
    assert "eur-lex.europa.eu" in result
    assert "Artikel 5" in result


def test_to_bibtex_format(ai_act_citation: Citation) -> None:
    formatter = CitationFormatter()
    result = formatter.to_bibtex(ai_act_citation)
    assert "@misc{" in result
    assert "32024R1689" in result

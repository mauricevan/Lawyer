"""Tests for article resolution and legal text trimming."""
from backend.src.utils.article_resolver import resolve_article_number
from backend.src.utils.legal_text_trimmer import trim_legal_preamble


def test_resolve_article_from_text() -> None:
    chunk = {"text": "Preamble noise. Artikel 52 lid 1 regelt dit."}
    assert resolve_article_number(chunk) == "52"


def test_trim_skips_long_preamble() -> None:
    preamble = "A" * 120
    text = f"{preamble} Artikel 5 bepaalt dat verwerking rechtmatig moet zijn."
    trimmed = trim_legal_preamble(text)
    assert trimmed.startswith("Artikel 5")


def test_citation_builder_resolves_article() -> None:
    from backend.src.services.citation_builder_service import CitationBuilderService

    chunks = [{"celex": "32024R1689", "text": "Artikel 50 verplicht transparantie.", "title": "AI Act"}]
    citations = CitationBuilderService().from_chunks(chunks)
    assert citations[0].article == "50"

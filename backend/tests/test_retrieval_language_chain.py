"""Tests for retrieval language fallback chain."""
from backend.src.utils.retrieval_language_chain import retrieval_language_chain


def test_french_chain_includes_nl_corpus_fallback() -> None:
    chain = retrieval_language_chain("fr")
    assert chain[0] == "fr"
    assert "en" in chain
    assert chain[-1] == "nl"


def test_dutch_chain_keeps_registry_order() -> None:
    chain = retrieval_language_chain("nl")
    assert chain[0] == "nl"
    assert "en" in chain


def test_chain_deduplicates_languages() -> None:
    chain = retrieval_language_chain("nl")
    assert len(chain) == len(set(chain))

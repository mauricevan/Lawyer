"""Tests for language registry loader."""
from ingestion.src.data.language_registry_loader import (
    get_cellar_uri,
    get_enabled_languages,
    get_fetch_fallback_chain,
    get_fts_config,
    load_language_registry,
)


def test_registry_includes_fr_de_es() -> None:
    registry = load_language_registry()
    assert registry["fr"].status == "go"
    assert registry["de"].status == "go"
    assert registry["es"].status == "go"


def test_fallback_chain_includes_english() -> None:
    chain = get_fetch_fallback_chain("fr")
    assert chain[0] == "fr"
    assert "en" in chain


def test_fts_and_cellar_mappings() -> None:
    assert get_fts_config("de") == "german"
    assert get_cellar_uri("es") == "SPA"


def test_enabled_languages_cover_rollout() -> None:
    enabled = get_enabled_languages()
    assert {"nl", "en", "fr", "de", "es"}.issubset(set(enabled))

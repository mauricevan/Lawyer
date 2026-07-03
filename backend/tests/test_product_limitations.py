"""Tests for localized product limitations (plan11 AC)."""
from shared.legal.product_limitations import get_product_limitations, supported_languages


def test_all_go_languages_have_limitations() -> None:
    for lang in supported_languages():
        items = get_product_limitations(lang)
        assert len(items) >= 3
        assert any("EUR-Lex" in item or "eur-lex" in item.lower() for item in items)


def test_unknown_language_falls_back_to_nl() -> None:
    nl = get_product_limitations("nl")
    fallback = get_product_limitations("xx")
    assert fallback == nl


def test_national_gap_messaging_present() -> None:
    for lang in ("nl", "en", "fr"):
        items = get_product_limitations(lang)
        combined = " ".join(items).lower()
        assert "national" in combined or "nationale" in combined or "nationales" in combined

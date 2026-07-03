"""Tests for plan11 AC compliance documentation and escalation parity."""
from pathlib import Path

import yaml

from shared.legal.disclaimers import get_disclaimer, get_escalation_text
from shared.legal.product_limitations import get_product_limitations, supported_languages

_REPO = Path(__file__).resolve().parents[2]
_LANGUAGES = ("nl", "en", "fr", "de", "es")


def test_national_gaps_registry_exists() -> None:
    path = _REPO / "docs/legal/national-implementation-gaps.yaml"
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    codes = {item["code"] for item in data["jurisdictions"]}
    assert {"NL", "FR", "DE", "ES"}.issubset(codes)


def test_escalation_path_has_required_sections() -> None:
    text = (_REPO / "docs/legal/escalation-path.md").read_text(encoding="utf-8")
    assert "Wanneer escaleren" in text
    assert "Stappen" in text


def test_disclaimer_escalation_limitations_parity() -> None:
    for lang in _LANGUAGES:
        assert get_disclaimer("layperson", lang)
        assert get_escalation_text("professional", lang)
        assert get_product_limitations(lang)
    assert supported_languages() == frozenset(_LANGUAGES)


def test_compliance_check_script_exists() -> None:
    assert (_REPO / "scripts/qa/run-legal-compliance-check.sh").is_file()

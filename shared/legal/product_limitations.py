"""Localized product limitation strings (plan11 AC)."""
from functools import lru_cache
from pathlib import Path
from typing import Literal

import yaml

Language = Literal["nl", "en", "fr", "de", "es"]
_CONFIG_PATH = Path(__file__).resolve().parents[1] / "config" / "product-limitations.yaml"
_SUPPORTED = frozenset({"nl", "en", "fr", "de", "es"})


@lru_cache(maxsize=1)
def _load_limitations() -> dict[str, tuple[str, ...]]:
    with open(_CONFIG_PATH, encoding="utf-8") as handle:
        data = yaml.safe_load(handle)
    return {
        lang: tuple(items)
        for lang, items in data.get("languages", {}).items()
    }


def get_product_limitations(language: str = "nl") -> tuple[str, ...]:
    """Return limitation bullets for the requested language."""
    lang = language.lower().split("-")[0]
    bundle = _load_limitations()
    if lang not in _SUPPORTED:
        lang = "nl"
    return bundle.get(lang, bundle["nl"])


def supported_languages() -> frozenset[str]:
    return _SUPPORTED

"""Load language registry for detection, FTS, and EUR-Lex fallbacks."""
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Literal

import yaml

LanguageStatus = Literal["go", "pilot", "disabled"]
_REGISTRY_PATH = Path(__file__).parent / "language_registry.yaml"


@dataclass(frozen=True)
class LanguageConfig:
    code: str
    label: str
    status: LanguageStatus
    fts_config: str
    cellar_uri: str
    fallback_chain: tuple[str, ...]


@lru_cache(maxsize=1)
def load_language_registry(path: Path | None = None) -> dict[str, LanguageConfig]:
    source = path or _REGISTRY_PATH
    with open(source, encoding="utf-8") as handle:
        data = yaml.safe_load(handle)
    output: dict[str, LanguageConfig] = {}
    for code, entry in data.get("languages", {}).items():
        output[code] = LanguageConfig(
            code=code,
            label=entry["label"],
            status=entry.get("status", "pilot"),
            fts_config=entry.get("fts_config", "simple"),
            cellar_uri=entry.get("cellar_uri", code.upper()[:3]),
            fallback_chain=tuple(entry.get("fallback_chain", [])),
        )
    return output


def get_enabled_languages() -> tuple[str, ...]:
    registry = load_language_registry()
    return tuple(code for code, cfg in registry.items() if cfg.status == "go")


def is_language_enabled(code: str) -> bool:
    registry = load_language_registry()
    config = registry.get(code.lower())
    return config is not None and config.status == "go"


def get_fts_config(code: str) -> str:
    registry = load_language_registry()
    config = registry.get(code.lower())
    return config.fts_config if config else "simple"


def get_cellar_uri(code: str) -> str:
    registry = load_language_registry()
    config = registry.get(code.lower())
    return config.cellar_uri if config else "ENG"


def get_fetch_fallback_chain(code: str) -> tuple[str, ...]:
    registry = load_language_registry()
    config = registry.get(code.lower())
    if not config:
        return ("en",)
    return (config.code, *config.fallback_chain)

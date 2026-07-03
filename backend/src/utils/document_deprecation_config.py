"""Load document deprecation register from shared config."""
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml

_REPO_ROOT = Path(__file__).resolve().parents[3]
_REGISTER_PATH = _REPO_ROOT / "shared/config/document_deprecation_register.yaml"


@dataclass(frozen=True, slots=True)
class DeprecationEntry:
    celex: str
    language: str | None
    status: str
    reason: str
    allow_explicit_celex: bool = True


@lru_cache(maxsize=1)
def load_document_deprecation_register() -> dict[str, Any]:
    with open(_REGISTER_PATH, encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def deprecation_policy() -> dict[str, Any]:
    register = load_document_deprecation_register()
    return register.get("policy", {})


@lru_cache(maxsize=1)
def load_deprecation_entries() -> tuple[DeprecationEntry, ...]:
    register = load_document_deprecation_register()
    loaded: list[DeprecationEntry] = []
    for row in register.get("entries", []):
        loaded.append(
            DeprecationEntry(
                celex=row["celex"],
                language=row.get("language"),
                status=row.get("status", "soft_deprecated"),
                reason=row.get("reason", ""),
                allow_explicit_celex=row.get("allow_explicit_celex", True),
            )
        )
    return tuple(loaded)

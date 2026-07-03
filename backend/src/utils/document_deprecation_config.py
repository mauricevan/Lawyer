"""Load document deprecation register from shared config."""
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml

_REPO_ROOT = Path(__file__).resolve().parents[3]
_REGISTER_PATH = _REPO_ROOT / "shared/config/document_deprecation_register.yaml"
VALID_STATUSES = frozenset({"soft_deprecated", "retired", "archived"})


@dataclass(frozen=True, slots=True)
class DeprecationEntry:
    celex: str
    language: str | None
    status: str
    reason: str
    allow_explicit_celex: bool = True


def validate_register_payload(register: dict[str, Any] | None) -> list[str]:
    """Return human-readable validation errors for a deprecation register payload."""
    if not register:
        return ["register payload is empty"]
    errors: list[str] = []
    seen: set[tuple[str, str | None]] = set()
    for index, row in enumerate(register.get("entries", [])):
        if not isinstance(row, dict):
            errors.append(f"entries[{index}] must be an object")
            continue
        celex = str(row.get("celex", "")).strip()
        if not celex:
            errors.append(f"entries[{index}]: missing celex")
            continue
        language = row.get("language")
        if language is not None and not str(language).strip():
            errors.append(f"entries[{index}]: language must be null or non-empty")
        status = row.get("status", "soft_deprecated")
        if status not in VALID_STATUSES:
            errors.append(f"entries[{index}]: invalid status '{status}'")
        key = (celex, str(language).strip() if language else None)
        if key in seen:
            errors.append(f"entries[{index}]: duplicate celex/language {key}")
        seen.add(key)
    return errors


@lru_cache(maxsize=1)
def load_document_deprecation_register() -> dict[str, Any]:
    if not _REGISTER_PATH.is_file():
        raise FileNotFoundError(f"Deprecation register not found: {_REGISTER_PATH}")
    with open(_REGISTER_PATH, encoding="utf-8") as handle:
        payload = yaml.safe_load(handle)
    if not isinstance(payload, dict):
        raise ValueError("Deprecation register root must be a mapping")
    errors = validate_register_payload(payload)
    if errors:
        raise ValueError(f"Invalid deprecation register: {'; '.join(errors)}")
    return payload


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
                celex=str(row["celex"]).strip(),
                language=row.get("language"),
                status=row.get("status", "soft_deprecated"),
                reason=row.get("reason", ""),
                allow_explicit_celex=bool(row.get("allow_explicit_celex", True)),
            )
        )
    return tuple(loaded)

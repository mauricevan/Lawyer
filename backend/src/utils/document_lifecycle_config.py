"""Load document lifecycle policy from shared config."""
from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml

_REPO_ROOT = Path(__file__).resolve().parents[3]
_CONFIG_PATH = _REPO_ROOT / "shared/config/document_lifecycle_policy.yaml"


@lru_cache(maxsize=1)
def load_document_lifecycle_policy() -> dict[str, Any]:
    with open(_CONFIG_PATH, encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def staleness_thresholds() -> dict[str, Any]:
    policy = load_document_lifecycle_policy()
    return policy.get("staleness", {})


def scan_gates() -> dict[str, int]:
    policy = load_document_lifecycle_policy()
    return {key: int(value) for key, value in policy.get("scan_gates", {}).items()}


def reindex_policy() -> dict[str, Any]:
    policy = load_document_lifecycle_policy()
    return policy.get("reindex", {})


def reindex_report_path() -> str:
    policy = load_document_lifecycle_policy()
    return str(
        policy.get("reindex_report", {}).get(
            "path", "docs/data/lifecycle-reports/reindex-latest.json"
        )
    )

"""Document version policy loader (plan13 AD). Owner: backend platform."""
from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml

_REPO_ROOT = Path(__file__).resolve().parents[3]
_POLICY_PATH = _REPO_ROOT / "shared/config/document_version_policy.yaml"


@lru_cache(maxsize=1)
def load_document_version_policy() -> dict[str, Any]:
    with open(_POLICY_PATH, encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def version_resolution_policy() -> dict[str, Any]:
    return load_document_version_policy().get("resolution", {})


def registered_version_families() -> list[dict[str, Any]]:
    return load_document_version_policy().get("registered_families", [])


def version_gate_policy() -> dict[str, Any]:
    return load_document_version_policy().get("gate", {})


def version_report_path() -> str:
    policy = load_document_version_policy()
    return str(policy.get("report", {}).get("path", "docs/data/lifecycle-reports/version-conflicts-latest.json"))

"""Policy registry loader (plan15 AA). Owner: backend platform."""
from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml

_REPO_ROOT = Path(__file__).resolve().parents[3]
_REGISTRY_PATH = _REPO_ROOT / "shared/config/policy_registry.yaml"


@lru_cache(maxsize=1)
def load_policy_registry() -> dict[str, Any]:
    with open(_REGISTRY_PATH, encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def repo_root() -> Path:
    return _REPO_ROOT


def policy_registry_report_path() -> str:
    registry = load_policy_registry()
    return str(registry.get("report", {}).get("path", "docs/data/governance-reports/policy-registry-latest.json"))

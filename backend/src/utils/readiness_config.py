"""Readiness policy loader (plan14 AA). Owner: backend platform."""
from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml

_REPO_ROOT = Path(__file__).resolve().parents[3]
_POLICY_PATH = _REPO_ROOT / "shared/config/readiness_policy.yaml"


@lru_cache(maxsize=1)
def load_readiness_policy() -> dict[str, Any]:
    with open(_POLICY_PATH, encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def dependency_policy(name: str) -> dict[str, Any]:
    policy = load_readiness_policy()
    return policy.get("dependencies", {}).get(name, {})

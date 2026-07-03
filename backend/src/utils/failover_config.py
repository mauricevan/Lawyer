"""Failover policy loader (plan14 AB). Owner: backend platform."""
from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml

_REPO_ROOT = Path(__file__).resolve().parents[3]
_POLICY_PATH = _REPO_ROOT / "shared/config/failover_policy.yaml"


@lru_cache(maxsize=1)
def load_failover_policy() -> dict[str, Any]:
    with open(_POLICY_PATH, encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def failover_report_path() -> str:
    policy = load_failover_policy()
    return str(policy.get("report", {}).get("path", "docs/data/reliability-reports/failover-latest.json"))

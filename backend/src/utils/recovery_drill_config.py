"""Recovery drill policy loader (plan14 AC). Owner: backend platform."""
from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml

_REPO_ROOT = Path(__file__).resolve().parents[3]
_POLICY_PATH = _REPO_ROOT / "shared/config/recovery_drill_policy.yaml"


@lru_cache(maxsize=1)
def load_recovery_drill_policy() -> dict[str, Any]:
    with open(_POLICY_PATH, encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def recovery_drill_report_path() -> str:
    policy = load_recovery_drill_policy()
    return str(policy.get("report", {}).get("path", "docs/data/reliability-reports/recovery-drill-latest.json"))

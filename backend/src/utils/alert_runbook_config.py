"""Alert-runbook policy loader (plan14 AD). Owner: backend platform."""
from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml

_REPO_ROOT = Path(__file__).resolve().parents[3]
_POLICY_PATH = _REPO_ROOT / "shared/config/alert_runbook_policy.yaml"


@lru_cache(maxsize=1)
def load_alert_runbook_policy() -> dict[str, Any]:
    with open(_POLICY_PATH, encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def repo_root() -> Path:
    return _REPO_ROOT


def incident_audit_report_path() -> str:
    policy = load_alert_runbook_policy()
    return str(policy.get("report", {}).get("path", "docs/data/reliability-reports/incident-playbook-audit-latest.json"))

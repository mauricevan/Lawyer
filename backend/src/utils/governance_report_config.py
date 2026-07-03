"""Governance report policy loader (plan15 AD)."""
from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml

_REPO = Path(__file__).resolve().parents[3]
_POLICY = _REPO / "shared/config/governance_report_policy.yaml"


@lru_cache(maxsize=1)
def load_governance_report_policy() -> dict[str, Any]:
    with open(_POLICY, encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def repo_root() -> Path:
    return _REPO

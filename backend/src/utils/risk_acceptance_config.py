"""Risk acceptance register loader (plan15 AB)."""
from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml

_REPO = Path(__file__).resolve().parents[3]
_REGISTER = _REPO / "shared/config/risk_acceptance_register.yaml"


@lru_cache(maxsize=1)
def load_risk_acceptance_register() -> dict[str, Any]:
    with open(_REGISTER, encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def repo_root() -> Path:
    return _REPO

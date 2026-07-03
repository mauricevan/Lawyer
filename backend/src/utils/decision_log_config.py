"""Decision log index loader (plan15 AC)."""
from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml

_REPO = Path(__file__).resolve().parents[3]
_INDEX = _REPO / "shared/config/decision_log_index.yaml"


@lru_cache(maxsize=1)
def load_decision_log_index() -> dict[str, Any]:
    with open(_INDEX, encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def repo_root() -> Path:
    return _REPO

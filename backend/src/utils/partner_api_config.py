"""Partner API policy loader (plan31 AA)."""
from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml

_REPO = Path(__file__).resolve().parents[3]
_POLICY = _REPO / "shared/config/partner_api_policy.yaml"


@lru_cache(maxsize=1)
def load_partner_api_policy() -> dict[str, Any]:
    with open(_POLICY, encoding="utf-8") as handle:
        return yaml.safe_load(handle)

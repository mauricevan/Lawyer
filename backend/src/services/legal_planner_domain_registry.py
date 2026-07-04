"""Domain-level CELEX routing from legal_source_planner_domains.yaml."""
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml

_REPO_ROOT = Path(__file__).resolve().parents[3]
_DOMAINS_PATH = _REPO_ROOT / "shared/config/legal_source_planner_domains.yaml"


@dataclass(frozen=True)
class DomainPlan:
    plan_id: str
    celex: str
    legal_domain: str | None
    triggers: tuple[str, ...]


def match_domain_plan(question: str) -> DomainPlan | None:
    """Return best domain plan when no article-specific plan matched."""
    lowered = question.lower()
    for entry in _load_domains():
        triggers = entry.get("triggers_any", [])
        if not _matches_triggers(lowered, triggers):
            continue
        return DomainPlan(
            plan_id=str(entry["id"]),
            celex=str(entry["celex"]),
            legal_domain=entry.get("legal_domain"),
            triggers=tuple(str(t) for t in triggers),
        )
    return None


def _matches_triggers(text: str, triggers: list[str]) -> bool:
    import re

    for trigger in triggers:
        if len(trigger) <= 5:
            if re.search(rf"\b{re.escape(trigger)}\b", text):
                return True
        elif trigger in text:
            return True
    return False


@lru_cache(maxsize=1)
def _load_domains() -> list[dict[str, Any]]:
    with open(_DOMAINS_PATH, encoding="utf-8") as handle:
        data = yaml.safe_load(handle)
    return list(data.get("domains", []))

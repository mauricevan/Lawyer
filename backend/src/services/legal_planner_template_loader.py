"""Load obligation templates for planner plans, domains, and CELEX fallbacks."""
from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml

_REPO_ROOT = Path(__file__).resolve().parents[3]
_TEMPLATES_PATH = _REPO_ROOT / "shared/config/legal_planner_obligation_templates.yaml"


def resolve_obligation_templates(
    plan_id: str,
    celex: str,
    legal_domain: str | None = None,
) -> list[dict[str, str]]:
    """Resolve templates: plan id → domain id → CELEX → legal_domain."""
    data = _load_templates()
    for key in (plan_id,):
        hit = _lookup(data.get("by_plan_id", {}), key)
        if hit:
            return hit
    hit = _lookup(data.get("by_domain_id", {}), plan_id)
    if hit:
        return hit
    hit = _lookup(data.get("by_celex", {}), celex)
    if hit:
        return hit
    if legal_domain:
        hit = _lookup(data.get("by_legal_domain", {}), legal_domain)
        if hit:
            return hit
    return []


def _lookup(section: dict[str, Any], key: str) -> list[dict[str, str]]:
    raw = section.get(key)
    if not raw:
        return []
    return [dict(row) for row in raw]


@lru_cache(maxsize=1)
def _load_templates() -> dict[str, Any]:
    with open(_TEMPLATES_PATH, encoding="utf-8") as handle:
        return yaml.safe_load(handle) or {}

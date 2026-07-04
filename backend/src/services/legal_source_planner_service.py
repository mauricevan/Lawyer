"""Legal source planner — question to CELEX + article targets (ADR-0009)."""
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml

from backend.src.services.celex_discovery_service import CelexCandidate
from backend.src.services.legal_planner_domain_registry import match_domain_plan
from backend.src.services.legal_planner_scoring import pick_best_explicit_plan

_REPO_ROOT = Path(__file__).resolve().parents[3]
_RULES_PATH = _REPO_ROOT / "shared/config/legal_source_planner.yaml"
_HIGH_DISCOVERY_SCORE = 0.75


@dataclass(frozen=True)
class LegalSourcePlan:
    plan_id: str
    celex: str
    articles: tuple[str, ...]
    related_celex: tuple[str, ...]
    legal_domain: str | None


class LegalSourcePlannerService:
    """Rule-based planner: juridische vraag → welke wet + welke artikelen lezen."""

    def plan(
        self,
        question: str,
        discovery_candidates: list[CelexCandidate] | None = None,
    ) -> LegalSourcePlan | None:
        lowered = question.lower()
        discovery_top3 = _discovery_celex_set(discovery_candidates)
        best = pick_best_explicit_plan(
            lowered, _load_explicit_plans(), discovery_celexes=discovery_top3,
        )
        if best:
            return _entry_to_plan(best)
        top = discovery_candidates[0] if discovery_candidates else None
        if top and top.score >= _HIGH_DISCOVERY_SCORE:
            return _discovery_plan(top)
        domain = match_domain_plan(question)
        if domain and top and top.score >= _HIGH_DISCOVERY_SCORE and domain.celex != top.celex:
            return _discovery_plan(top)
        if domain:
            return LegalSourcePlan(
                plan_id=domain.plan_id,
                celex=domain.celex,
                articles=(),
                related_celex=(),
                legal_domain=domain.legal_domain,
            )
        if top and top.score >= 0.5:
            return _discovery_plan(top)
        return None


def _discovery_celex_set(candidates: list[CelexCandidate] | None) -> frozenset[str]:
    if not candidates:
        return frozenset()
    return frozenset(
        candidate.celex for candidate in candidates[:3] if candidate.score >= 0.5
    )


def _discovery_plan(candidate: CelexCandidate) -> LegalSourcePlan:
    return LegalSourcePlan(
        plan_id="discovery",
        celex=candidate.celex,
        articles=(),
        related_celex=(),
        legal_domain=None,
    )


def _entry_to_plan(entry: dict[str, Any]) -> LegalSourcePlan:
    return LegalSourcePlan(
        plan_id=str(entry["id"]),
        celex=str(entry["celex"]),
        articles=tuple(str(a) for a in entry.get("articles", [])),
        related_celex=tuple(str(c) for c in entry.get("related_celex", [])),
        legal_domain=entry.get("legal_domain"),
    )


@lru_cache(maxsize=1)
def _load_explicit_plans() -> list[dict[str, Any]]:
    with open(_RULES_PATH, encoding="utf-8") as handle:
        data = yaml.safe_load(handle)
    return list(data.get("plans", []))

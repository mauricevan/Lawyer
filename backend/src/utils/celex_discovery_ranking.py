"""Generic legal_domain-aware CELEX discovery ranking — domain-first (V2)."""
from functools import lru_cache
from pathlib import Path
from typing import TYPE_CHECKING, Any

import yaml

from backend.src.services.legal_question_classifier_service import classify_legal_question
from backend.src.utils.legal_domain_retrieval_filter import is_celex_allowed_for_domain

if TYPE_CHECKING:
    from backend.src.services.celex_discovery_service import CelexCandidate

_REPO_ROOT = Path(__file__).resolve().parents[3]
_PLANS_PATH = _REPO_ROOT / "shared/config/legal_source_planner.yaml"
_DOMAINS_PATH = _REPO_ROOT / "shared/config/legal_source_planner_domains.yaml"
_DOMAIN_BOOST = 0.2
_DOMAIN_PENALTY = 0.15
_ROUTING_YAML_PREFERENCE: dict[str, frozenset[str]] = {
    "employment_law": frozenset({"employment"}),
    "consumer_protection": frozenset({"consumer", "transport"}),
    "product_safety": frozenset({"consumer", "environment"}),
    "administrative_law": frozenset({"consumer"}),
    "internal_market": frozenset(),
    "data_protection": frozenset({"privacy"}),
    "digital_services": frozenset(),
}


def rank_discovery_by_legal_context(
    candidates: list["CelexCandidate"],
    question: str,
) -> list["CelexCandidate"]:
    """Re-rank and filter discovery hits using routing legal_domain."""
    from backend.src.services.celex_discovery_service import CelexCandidate

    classification = classify_legal_question(question)
    domain = classification.legal_domain
    allowed = [
        candidate for candidate in candidates
        if is_celex_allowed_for_domain(candidate.celex, domain)
    ]
    pool = allowed or list(candidates)
    preferred = _ROUTING_YAML_PREFERENCE.get(domain, frozenset())
    domain_map = _load_celex_domain_map()
    known_domains = frozenset(domain_map.values())
    adjusted: list[CelexCandidate] = []
    for candidate in pool:
        yaml_domain = domain_map.get(candidate.celex)
        score = candidate.score
        if yaml_domain in preferred:
            score = min(1.0, score + _DOMAIN_BOOST)
        elif yaml_domain in known_domains and preferred and yaml_domain not in preferred:
            score = max(0.0, score - _DOMAIN_PENALTY)
        adjusted.append(
            CelexCandidate(
                celex=candidate.celex,
                score=score,
                source=candidate.source,
                title=candidate.title,
            )
        )
    return sorted(adjusted, key=lambda item: item.score, reverse=True)


@lru_cache(maxsize=1)
def _load_celex_domain_map() -> dict[str, str]:
    mapping: dict[str, str] = {}
    for path in (_PLANS_PATH, _DOMAINS_PATH):
        entries = _yaml_entries(path)
        for entry in entries:
            celex = str(entry.get("celex", ""))
            yaml_domain = entry.get("legal_domain")
            if celex and yaml_domain:
                mapping[celex] = str(yaml_domain)
    return mapping


def _yaml_entries(path: Path) -> list[dict[str, Any]]:
    with open(path, encoding="utf-8") as handle:
        data = yaml.safe_load(handle)
    key = "plans" if "plans" in data else "domains"
    return list(data.get(key, []))

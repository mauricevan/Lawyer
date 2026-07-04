"""Score CELEX candidates against V4 conflict + domain — V5.1."""
from dataclasses import dataclass

from backend.src.utils.conflict_celex_registry import (
    is_celex_allowed_for_conflict_type,
    primary_celex_for_conflict,
)
from backend.src.utils.conflict_domain_mapping import map_conflict_to_domain
from backend.src.utils.effect_law_mapping import map_effect_to_law
from backend.src.utils.legal_domain_retrieval_filter import is_celex_allowed_for_domain
from shared.schemas.legal_conflict import LegalCaseAnalysis, PrimaryLegalConflict

_MIN_VALID_SCORE = 60
_MAX_INSTRUMENTS = 3


@dataclass(frozen=True)
class ScoredCelex:
    """CELEX with conflict-aware relevance score."""

    celex: str
    score: int
    name: str


def score_celex_candidates(
    analysis: LegalCaseAnalysis,
    candidate_celexes: list[str],
) -> list[ScoredCelex]:
    """Score and rank CELEX; highest first."""
    locked = map_conflict_to_domain(analysis.primary_legal_conflict)
    scored: list[ScoredCelex] = []
    seen: set[str] = set()
    for celex in candidate_celexes:
        if not celex or celex in seen:
            continue
        seen.add(celex)
        score = _score_one(celex, analysis, locked.domain)
        if score <= -50:
            continue
        scored.append(ScoredCelex(celex=celex, score=score, name=_instrument_name(celex, analysis)))
    scored.sort(key=lambda item: item.score, reverse=True)
    return scored


def pick_final_celex(scored: list[ScoredCelex]) -> tuple[list[ScoredCelex], bool]:
    """Return top instruments; flag domain re-retrieval when no score >= 60."""
    valid = [item for item in scored if item.score >= _MIN_VALID_SCORE]
    if valid:
        return valid[:_MAX_INSTRUMENTS], False
    if scored:
        return scored[:_MAX_INSTRUMENTS], True
    return [], True


def _score_one(celex: str, analysis: LegalCaseAnalysis, locked_domain: str) -> int:
    conflict = analysis.primary_legal_conflict
    if not is_celex_allowed_for_conflict_type(celex, conflict):
        return -100
    if not is_celex_allowed_for_domain(celex, locked_domain):  # type: ignore[arg-type]
        return -100
    score = 0
    score += 40
    if celex in primary_celex_for_conflict(conflict):
        score += 30
    if analysis.default_celex and celex == analysis.default_celex:
        score += 15
    if _framework_matches(celex, analysis.likely_eu_frameworks):
        score += 20
    score += _actor_bonus(celex, analysis)
    if _is_enforcement_only(celex) and analysis.legal_question_type != "enforcement":
        score -= 50
    if conflict == "internal_market_restriction" and celex == "32008R0768":
        if _has_ecommerce_framework(analysis.likely_eu_frameworks):
            score -= 25
    if analysis.legal_effect:
        effect_mapping = map_effect_to_law(analysis.legal_effect, conflict)
        if celex == effect_mapping.primary_celex:
            score += 25
        if celex in effect_mapping.secondary_celex:
            score += 10
    return score


def _framework_matches(celex: str, frameworks: list[str]) -> bool:
    hints = {
        "32000L0031": ("2000/31", "e-commerce", "ecommerce"),
        "32011L0083": ("2011/83", "consumer"),
        "32000L0078": ("2000/78", "employment"),
        "32016R0679": ("2016/679", "gdpr"),
        "32023R0988": ("2023/988", "gpsr"),
        "32019R1020": ("2019/1020", "surveillance"),
        "32022R2065": ("2022/2065", "digital services"),
        "32008R0768": ("764/2008", "mutual recognition"),
    }
    joined = " ".join(frameworks).lower()
    return any(h in joined for h in hints.get(celex, ()))


def _has_ecommerce_framework(frameworks: list[str]) -> bool:
    joined = " ".join(frameworks).lower()
    return "2000/31" in joined or "e-commerce" in joined


def _actor_bonus(celex: str, analysis: LegalCaseAnalysis) -> int:
    actor = analysis.legal_actor
    if actor in {"authority", "unknown"} and celex in {"32000L0031", "32008R0768"}:
        return 10
    if actor == "consumer" and celex == "32011L0083":
        return 20
    if actor == "employee" and celex == "32000L0078":
        return 20
    return 0


def _is_enforcement_only(celex: str) -> bool:
    return celex in {"32019R1020", "32013R0952"}


def _instrument_name(celex: str, analysis: LegalCaseAnalysis) -> str:
    if analysis.default_celex == celex and analysis.likely_eu_frameworks:
        return analysis.likely_eu_frameworks[0][:64]
    names = {
        "32000L0031": "ecommerce_country_of_origin",
        "32008R0768": "internal_market_mutual_recognition",
        "32011L0083": "consumer_rights",
        "32000L0078": "equal_treatment_employment",
        "32016R0679": "gdpr",
        "32023R0988": "gpsr",
        "32019R1020": "market_surveillance",
        "32022R2065": "dsa_obligations",
    }
    return names.get(celex, "EU-regelgeving")

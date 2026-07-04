"""Merge legal hypothesis / case analysis into interpretation plan."""
from backend.src.utils.conflict_domain_mapping import map_conflict_to_domain
from backend.src.utils.domain_framework_registry import celex_from_frameworks
from backend.src.utils.legal_domain_retrieval_filter import filter_instruments_by_domain
from shared.schemas.legal_conflict import LegalCaseAnalysis
from shared.schemas.legal_hypothesis import LegalHypothesis
from shared.schemas.legal_interpretation import InstrumentTarget, LegalInterpretationPlan


def merge_case_analysis_into_plan(
    plan: LegalInterpretationPlan,
    analysis: LegalCaseAnalysis,
) -> LegalInterpretationPlan:
    """V4: domain always from conflict mapping — planner cannot override."""
    instruments = filter_instruments_by_domain(plan.instruments, analysis.legal_domain)
    instruments = _ensure_default_celex(
        instruments,
        analysis.default_celex,
        analysis.likely_eu_frameworks,
    )
    return plan.model_copy(update={
        "legal_actor": analysis.legal_actor,
        "legal_domain": analysis.legal_domain,
        "legal_question_type": analysis.legal_question_type,
        "instruments": instruments,
        "search_keywords": _framework_keywords_from_list(analysis.likely_eu_frameworks, plan.search_keywords),
        "reasoning_brief": analysis.case_summary[:200],
    })


def merge_hypothesis_into_plan(
    plan: LegalInterpretationPlan,
    hypothesis: LegalHypothesis,
) -> LegalInterpretationPlan:
    """Prefer V4 conflict-mapped domain over keyword-derived planner output."""
    if hypothesis.primary_legal_conflict:
        mapping = map_conflict_to_domain(hypothesis.primary_legal_conflict)
        domain = mapping.domain
        frameworks = list(hypothesis.likely_eu_frameworks) or list(mapping.frameworks)
        default_celex = mapping.default_celex
    else:
        domain = _prefer(hypothesis.legal_domain_guess, plan.legal_domain)
        frameworks = hypothesis.likely_eu_frameworks
        default_celex = celex_from_frameworks(frameworks)
    actor = _prefer(hypothesis.legal_actor, plan.legal_actor)
    question_type = _prefer(hypothesis.legal_question_type, plan.legal_question_type)
    instruments = filter_instruments_by_domain(plan.instruments, domain)
    instruments = _ensure_default_celex(instruments, default_celex, frameworks)
    if not instruments:
        instruments = _ensure_framework_instrument(instruments, hypothesis)
    return plan.model_copy(update={
        "legal_actor": actor,
        "legal_domain": domain,
        "legal_question_type": question_type,
        "instruments": instruments,
        "search_keywords": _framework_keywords(hypothesis, plan.search_keywords),
        "reasoning_brief": (hypothesis.case_summary or hypothesis.legal_problem)[:200],
    })


def _ensure_framework_instrument(
    instruments: list[InstrumentTarget],
    hypothesis: LegalHypothesis,
) -> list[InstrumentTarget]:
    if instruments:
        return instruments
    celex = celex_from_frameworks(hypothesis.likely_eu_frameworks)
    if not celex:
        return instruments
    name = hypothesis.likely_eu_frameworks[0][:64] if hypothesis.likely_eu_frameworks else "EU-regelgeving"
    return [InstrumentTarget(name=name, celex=celex, articles=[], confidence=0.6)]


def _prefer(hypothesis_value: str, plan_value: str) -> str:
    if hypothesis_value != "unknown":
        return hypothesis_value
    return plan_value


def _framework_keywords(hypothesis: LegalHypothesis, existing: list[str]) -> list[str]:
    return _framework_keywords_from_list(hypothesis.likely_eu_frameworks, existing)


def _framework_keywords_from_list(frameworks: list[str], existing: list[str]) -> list[str]:
    from_frameworks = [
        token
        for framework in frameworks
        for token in framework.lower().split()
        if len(token) > 4
    ][:6]
    merged = list(dict.fromkeys([*from_frameworks, *[k.lower() for k in existing if k]]))
    return merged[:8]


def _ensure_default_celex(
    instruments: list[InstrumentTarget],
    default_celex: str | None,
    frameworks: list[str],
) -> list[InstrumentTarget]:
    if instruments:
        return instruments
    celex = default_celex or celex_from_frameworks(frameworks)
    if not celex:
        return instruments
    name = frameworks[0][:64] if frameworks else "EU-regelgeving"
    return [InstrumentTarget(name=name, celex=celex, articles=[], confidence=0.65)]

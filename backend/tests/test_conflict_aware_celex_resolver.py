"""Tests for V5.1 conflict-aware CELEX resolver."""
from backend.src.services.conflict_aware_celex_resolver_service import ConflictAwareCelexResolverService
from backend.src.services.legal_hypothesis_service import LegalHypothesisService
from backend.src.services.primary_legal_conflict_service import select_primary_legal_conflict
from backend.src.utils.conflict_domain_mapping import map_conflict_to_domain
from shared.schemas.legal_conflict import LegalCaseAnalysis
from shared.schemas.legal_interpretation import InstrumentTarget, LegalInterpretationPlan

PLATFORM_ADS_Q = (
    "Mag een EU-lidstaat eisen dat online platforms die advertenties tonen aan consumenten "
    "verplicht zijn om vooraf alle adverteerders te verifiëren en alleen toe te laten "
    "als zij in de EU gevestigd zijn? En welke EU-regels bepalen of zo'n nationale eis is toegestaan?"
)


def _analysis_for(question: str) -> LegalCaseAnalysis:
    hypothesis = LegalHypothesisService()._rule_hypothesis(question)
    conflict = select_primary_legal_conflict(question, hypothesis)
    mapping = map_conflict_to_domain(conflict)
    return LegalCaseAnalysis(
        case_summary=hypothesis.legal_problem,
        primary_legal_conflict=conflict,
        legal_domain=mapping.domain,
        legal_actor=hypothesis.legal_actor,
        legal_question_type="national_measure",
        likely_eu_frameworks=list(mapping.frameworks),
        default_celex=mapping.default_celex,
    )


def test_platform_ads_rejects_planner_768_prefers_2000_31():
    analysis = _analysis_for(PLATFORM_ADS_Q)
    plan = LegalInterpretationPlan(
        legal_domain="internal_market",
        legal_question_type="national_measure",
        instruments=[
            InstrumentTarget(
                name="internal_market_national_rules",
                celex="32008R0768",
                articles=["1", "2"],
                confidence=0.7,
            ),
        ],
    )
    result = ConflictAwareCelexResolverService().resolve(analysis, plan)
    assert result.final_celex[0] == "32000L0031"
    assert "32008R0768" not in result.final_celex
    assert result.confidence >= 0.6
    assert result.final_domain == "internal_market"


def test_forbidden_consumer_celex_rejected_for_internal_market():
    analysis = _analysis_for(PLATFORM_ADS_Q)
    plan = LegalInterpretationPlan(
        legal_domain="internal_market",
        instruments=[InstrumentTarget(name="consumer_rights", celex="32011L0083", articles=[], confidence=0.5)],
    )
    result = ConflictAwareCelexResolverService().resolve(analysis, plan)
    assert "32011L0083" in result.rejected_celex
    assert result.rejection_reason == "forbidden_for_conflict"
    assert "32000L0031" in result.final_celex

"""Tests for V6 legal effect engine."""
from backend.src.services.legal_effect_service import LegalEffectService
from backend.src.utils.effect_law_mapping import apply_effect_to_case_analysis, map_effect_to_law
from backend.src.utils.hypothesis_retrieval_query import build_analysis_retrieval_query
from shared.schemas.legal_conflict import LegalCaseAnalysis

PLATFORM_ADS_Q = (
    "Mag een EU-lidstaat eisen dat online platforms die advertenties tonen aan consumenten "
    "verplicht zijn om vooraf alle adverteerders te verifiëren en alleen toe te laten "
    "als zij in de EU gevestigd zijn?"
)


def _base_analysis() -> LegalCaseAnalysis:
    return LegalCaseAnalysis(
        case_summary=PLATFORM_ADS_Q,
        primary_legal_conflict="internal_market_restriction",
        legal_domain="internal_market",
        legal_question_type="national_measure",
        likely_eu_frameworks=["TFEU free movement"],
        default_celex="32000L0031",
    )


def test_platform_ads_discrimination_by_establishment():
    analysis = _base_analysis()
    effect = LegalEffectService().classify(PLATFORM_ADS_Q, analysis)
    assert effect.legal_effect_type == "discrimination_by_establishment"
    assert effect.state_action == "eligibility_requirement"
    assert effect.restriction_strength == "high"
    assert effect.effect_conclusion_hint == "prohibited"


def test_effect_maps_to_ecommerce_celex():
    analysis = _base_analysis()
    effect = LegalEffectService().classify(PLATFORM_ADS_Q, analysis)
    enriched = apply_effect_to_case_analysis(analysis.model_copy(update={"legal_effect": effect}))
    mapping = map_effect_to_law(effect, analysis.primary_legal_conflict)
    assert enriched.default_celex == "32000L0031"
    assert mapping.primary_celex == "32000L0031"


def test_retrieval_query_includes_effect_type():
    analysis = _base_analysis()
    effect = LegalEffectService().classify(PLATFORM_ADS_Q, analysis)
    enriched = apply_effect_to_case_analysis(analysis.model_copy(update={"legal_effect": effect}))
    query = build_analysis_retrieval_query(enriched)
    assert "discrimination by establishment" in query
    assert "internal market restriction" in query

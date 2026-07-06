"""Tests for compact declarant answer formatting."""
from backend.src.services.declarant_plan_builder_service import DeclarantPlanBuilderService
from backend.src.services.evidence_validation_service import EvidenceValidationService
from backend.src.services.legal_hypothesis_service import LegalHypothesisService
from backend.src.services.primary_legal_conflict_service import select_primary_legal_conflict
from backend.src.utils.conflict_domain_mapping import map_conflict_to_domain
from backend.src.utils.declarant_answer_formatter import build_declarant_verified_answer
from shared.schemas.declarant_dossier import DeclarantPhase, DeclarantThinkResult
from shared.schemas.legal_conflict import LegalCaseAnalysis

_MERGED = "mag ik een platform bouwen — verduidelijking: contentwebsite"
_DSA_CHUNKS = [
    {
        "celex": "32022R2065",
        "article_number": "3",
        "text": (
            "This Regulation lays down harmonised rules on the provision of intermediary "
            "services, in particular online platforms, in the internal market."
        ),
        "title": "Digital Services Act",
    },
]


def _platform_plan():
    hypothesis = LegalHypothesisService()._rule_hypothesis(_MERGED)
    conflict = select_primary_legal_conflict(_MERGED, hypothesis)
    mapping = map_conflict_to_domain(conflict)
    analysis = LegalCaseAnalysis(
        case_summary="online platform starten",
        parties=[],
        context="EU",
        possible_domains=["digital_services"],
        primary_legal_conflict=conflict,
        legal_domain=mapping.domain,
        legal_actor="unknown",
        legal_question_type="market_access",
        likely_eu_frameworks=list(mapping.frameworks),
        default_celex=mapping.default_celex,
    )
    think = DeclarantThinkResult(
        phase=DeclarantPhase.FETCH,
        ready_to_search=True,
        effective_question=_MERGED,
        user_goal="platform starten",
        analysis=analysis,
        hypothesis_celex=("32022R2065",),
        articles_by_celex={"32022R2065": ("3",)},
    )
    return DeclarantPlanBuilderService().build(think), hypothesis, analysis


def test_evidence_accepts_dsa_chunks_for_platform_plan():
    plan, hypothesis, analysis = _platform_plan()
    result = EvidenceValidationService().validate(
        _MERGED, _DSA_CHUNKS, plan, hypothesis, analysis,
    )
    assert result.is_valid


def test_declarant_answer_contains_de_wet_zegt_and_article():
    answer = build_declarant_verified_answer(_MERGED, _DSA_CHUNKS)
    assert answer is not None
    lowered = answer.lower()
    assert "de wet zegt" in lowered
    assert "artikel 3" in lowered
    assert "32022r2065" in lowered or "digital services" in lowered

"""Unit tests for declarant think/plan routing (no EUR-Lex)."""
from __future__ import annotations

from backend.src.services.legal_source_planner_service import LegalSourcePlannerService
from backend.src.services.rag_service import RagService
from shared.schemas.query import QueryRequest


def test_planner_customs_territory_targets():
    planner = LegalSourcePlannerService()
    source = planner.plan("Welke lidstaten maken deel uit van de douane-unie?")
    assert source is not None
    assert source.celex == "32013R0952"
    assert "4" in source.articles
    assert "12016E028" in source.related_celex


def test_planner_gpsr_supplier_docs():
    planner = LegalSourcePlannerService()
    source = planner.plan("Mag mijn werkgever GPSR-documenten van de leverancier eisen?")
    assert source is not None
    assert source.celex == "32023R0988"


def test_planner_identity_legitimation():
    planner = LegalSourcePlannerService()
    source = planner.plan("Moet ik me legitimeren bij een EU-overheidsdienst?")
    assert source is not None
    assert source.celex == "32004L0038"
    assert "32014R0910" in source.related_celex


def test_classify_customs_domain_for_territory_question():
    from backend.src.services.legal_question_classifier_service import classify_legal_question

    result = classify_legal_question("Welke lidstaten maken deel uit van de douane-unie?")
    assert result.legal_domain == "customs_law"


def test_planner_china_import_declaration():
    planner = LegalSourcePlannerService()
    question = (
        "Ik verkoop via webshop kleine pakketjes vanuit China naar NL onder 150 euro. "
        "Moet ik douaneaangifte doen?"
    )
    source = planner.plan(question)
    assert source is not None
    assert source.plan_id == "ucc_import_declaration"
    assert "156" in source.articles


def test_ambiguity_customs_territory_clear():
    from backend.src.services.legal_ambiguity_detector_service import LegalAmbiguityDetectorService

    state, _score, _reasons = LegalAmbiguityDetectorService().detect(
        "Welke lidstaten maken deel uit van het douanegebied van de douane-unie?",
    )
    assert state == "clear"


def test_ambiguity_gpsr_supplier_clear():
    from backend.src.services.legal_ambiguity_detector_service import LegalAmbiguityDetectorService

    state, _score, _reasons = LegalAmbiguityDetectorService().detect(
        "Mag mijn werkgever van mij GPSR-documenten van de leverancier eisen?",
    )
    assert state == "clear"


def test_ambiguity_vague_customs_question():
    from backend.src.services.legal_ambiguity_detector_service import LegalAmbiguityDetectorService

    state, _score, _reasons = LegalAmbiguityDetectorService().detect("Moet ik douaneaangifte doen?")
    assert state == "ambiguous"


def test_rag_prefers_declarant_over_vague():
    service = RagService()
    request = QueryRequest(
        question="Moet ik douaneaangifte doen?",
        audience="layperson",
        language="nl",
    )
    assert service._should_use_declarant(request) is True


def test_planner_platform_contentwebsite_targets_dsa():
    planner = LegalSourcePlannerService()
    merged = "mag ik een platform bouwen — verduidelijking: contentwebsite"
    source = planner.plan(merged)
    assert source is not None
    assert source.celex == "32022R2065"


def test_plan_builder_platform_uses_digital_services_domain():
    from backend.src.services.declarant_plan_builder_service import DeclarantPlanBuilderService
    from backend.src.services.legal_hypothesis_service import LegalHypothesisService
    from backend.src.services.primary_legal_conflict_service import select_primary_legal_conflict
    from backend.src.utils.conflict_domain_mapping import map_conflict_to_domain
    from shared.schemas.declarant_dossier import DeclarantPhase, DeclarantThinkResult
    from shared.schemas.legal_conflict import LegalCaseAnalysis

    merged = "mag ik een platform bouwen — verduidelijking: contentwebsite"
    hypothesis = LegalHypothesisService()._rule_hypothesis(merged)
    conflict = select_primary_legal_conflict(merged, hypothesis)
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
        effective_question=merged,
        user_goal="platform starten",
        analysis=analysis,
        hypothesis_celex=("32022R2065",),
        articles_by_celex={"32022R2065": ("3", "14")},
    )
    plan = DeclarantPlanBuilderService().build(think)
    assert plan.legal_domain == "digital_services"
    assert any(inst.celex == "32022R2065" for inst in plan.instruments)

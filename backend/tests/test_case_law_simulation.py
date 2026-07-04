"""Tests for V8.1 structured case law simulation."""
from backend.src.services.case_law_revision_service import CaseLawRevisionService
from backend.src.services.case_law_simulation_gate_service import CaseLawSimulationGateService
from backend.src.services.court_simulation_service import CourtSimulationService
from backend.src.services.legal_effect_service import LegalEffectService
from backend.src.utils.proportionality_engine import assess_proportionality
from backend.src.utils.structured_judgment_formatter import (
    format_structured_judgment,
    validate_structured_judgment_text,
)
from shared.schemas.legal_conflict import LegalCaseAnalysis

PLATFORM_ADS_Q = (
    "Mag een EU-lidstaat eisen dat online platforms advertenties tonen en alleen adverteerders "
    "in de EU toelaten?"
)


def _analysis() -> LegalCaseAnalysis:
    base = LegalCaseAnalysis(
        case_summary=PLATFORM_ADS_Q,
        context="e-commerce platform adverteerders EU gevestigd",
        primary_legal_conflict="internal_market_restriction",
        legal_domain="internal_market",
        legal_question_type="national_measure",
        likely_eu_frameworks=["Directive 2000/31/EC"],
        default_celex="32000L0031",
    )
    effect = LegalEffectService().classify(PLATFORM_ADS_Q, base)
    return base.model_copy(update={"legal_effect": effect})


def test_proportionality_has_all_three_steps():
    analysis = _analysis()
    result = assess_proportionality(analysis)
    assert result.is_complete is True
    assert result.suitability_text
    assert result.necessity_text
    assert result.balancing_text
    assert result.passes_overall is False


def test_structured_judgment_has_seven_sections():
    analysis = _analysis()
    answer = "## Kort antwoord\n**In beginsel niet toegestaan**.\n\n## Juridische basis\nArtikel 3."
    simulation = CourtSimulationService().simulate(analysis, answer, ["32000L0031"])
    assert simulation.structured_judgment is not None
    assert simulation.structure_valid is True
    assert simulation.structure_enforcement == "pass"
    text = simulation.formatted_judgment
    assert "### 1. Issue" in text
    assert "### 7. Legal Effect Classification" in text
    assert "#### 5.1 Suitability" in text
    assert "#### 5.3 Balancing" in text
    assert validate_structured_judgment_text(text, simulation.structured_judgment)


def test_issue_is_legal_question_not_description():
    analysis = _analysis()
    simulation = CourtSimulationService().simulate(analysis, "", ["32000L0031"])
    issue = simulation.structured_judgment.issue
    assert issue.startswith("Whether")
    assert "Article 56 TFEU" in issue


def test_platform_ads_prohibited_restriction():
    analysis = _analysis()
    simulation = CourtSimulationService().simulate(analysis, "", ["32000L0031"])
    assert simulation.court_simulation_result == "incompatible_with_eu_law"
    assert simulation.structured_judgment.legal_effect_classification in {
        "prohibited restriction",
        "justified but disproportionate restriction",
    }
    assert "disproportionate restriction incompatible" in simulation.structured_judgment.court_conclusion


def test_no_free_text_intro_in_formatted_judgment():
    analysis = _analysis()
    simulation = CourtSimulationService().simulate(analysis, "", ["32000L0031"])
    body_before_conclusion = simulation.formatted_judgment.split("### 6. Court Conclusion")[0].lower()
    assert "in beginsel niet toegestaan" not in body_before_conclusion
    assert "de eu-rechter zou waarschijnlijk" not in body_before_conclusion


def test_gate_injects_structured_hof_simulatie():
    analysis = _analysis()
    bundle = {
        "answer_text": "## Kort antwoord\n**Ja**, toegestaan.\n\n## Juridische basis\nArtikel 3.",
        "citations": [{"celex": "32000L0031"}],
        "coverage_status": "sufficient",
    }
    revised_bundle, simulation = CaseLawSimulationGateService().gate(bundle, analysis)
    assert simulation is not None
    assert "### 1. Issue" in revised_bundle["answer_text"]
    assert "### 6. Court Conclusion" in revised_bundle["answer_text"]
    assert simulation.structured_judgment.legal_effect_classification


def test_revision_uses_court_conclusion_not_narrative():
    analysis = _analysis()
    answer = "## Kort antwoord\n**Ja**, toegestaan.\n\n## Juridische basis\nArtikel 3."
    simulation = CourtSimulationService().simulate(analysis, answer, ["32000L0031"])
    revised = CaseLawRevisionService().revise(answer, simulation, analysis)
    kort = revised.split("## Kort antwoord")[1].split("##")[0].lower()
    assert "in beginsel niet toegestaan" not in kort
    assert "disproportionate restriction" in kort or "incompatible" in kort

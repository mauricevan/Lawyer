"""Tests for V7 adversarial legal judge."""
from backend.src.services.adversarial_legal_judge_service import AdversarialLegalJudgeService
from backend.src.services.legal_effect_service import LegalEffectService
from backend.src.services.legal_judge_revision_service import LegalJudgeRevisionService
from backend.src.utils.legal_judge_checks import run_all_judge_checks
from shared.schemas.legal_conflict import LegalCaseAnalysis
from shared.schemas.legal_interpretation import LegalInterpretationPlan

PLATFORM_ADS_Q = (
    "Mag een EU-lidstaat eisen dat online platforms advertenties tonen en alleen adverteerders "
    "in de EU toelaten?"
)


def _analysis() -> LegalCaseAnalysis:
    base = LegalCaseAnalysis(
        case_summary=PLATFORM_ADS_Q,
        primary_legal_conflict="internal_market_restriction",
        legal_domain="internal_market",
        legal_question_type="national_measure",
        likely_eu_frameworks=["Directive 2000/31/EC"],
        default_celex="32000L0031",
    )
    effect = LegalEffectService().classify(PLATFORM_ADS_Q, base)
    return base.model_copy(update={"legal_effect": effect})


def test_judge_fails_absolute_no_answer():
    analysis = _analysis()
    answer = "## Kort antwoord\n**Nee.** De lidstaat mag dit niet.\n\n## Juridische basis\nArtikel 3."
    plan = LegalInterpretationPlan(legal_domain="internal_market", legal_question_type="national_measure")
    verdict = AdversarialLegalJudgeService().review(answer, analysis, plan, [], ["32000L0031"])
    assert verdict.pass_fail == "fail"
    assert verdict.severity in {"medium", "high"}
    assert "missing_exception_analysis" in verdict.issues_found or "overconfident_conclusion" in verdict.issues_found


def test_revision_adds_exception_nuance():
    analysis = _analysis()
    bad = "## Kort antwoord\n**Nee.** De lidstaat mag dit niet.\n\n## Juridische basis\nArtikel 3."
    revised = LegalJudgeRevisionService().revise(
        bad,
        ["missing_exception_analysis", "overconfident_conclusion"],
        analysis,
    )
    assert "uitzondering" in revised.lower() or "in beginsel" in revised.lower()


def test_judge_passes_nuanced_answer():
    analysis = _analysis()
    answer = (
        "## Kort antwoord\n**In beginsel niet toegestaan**, tenzij de maatregel evenredig is.\n\n"
        "## Juridisch effect\nDe maatregel discrimineert op vestiging.\n\n"
        "## Uitzonderingen en nuance\nEen uitzondering is mogelijk bij gerechtvaardigde doelen.\n\n"
        "## Juridische basis\nArtikel 3."
    )
    chunks = [{"text": "Member States shall not restrict information society services country of origin", "celex": "32000L0031"}]
    plan = LegalInterpretationPlan(legal_domain="internal_market")
    findings = run_all_judge_checks(answer, analysis, plan, chunks, ["32000L0031"])
    high = [f for f in findings if f.severity == "high"]
    assert not high

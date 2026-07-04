"""Professional-mode AVG rechtsgronden (art. 6) regression."""
from backend.src.services.legal_source_planner_service import LegalSourcePlannerService
from backend.src.services.question_intent_service import QuestionIntentService

QUESTION = (
    "en organisatie wil persoonsgegevens verwerken zonder toestemming van de betrokkenen. "
    "Op welke rechtsgronden kan dit volgens Verordening (EU) 2016/679 (AVG), "
    "welke voorwaarden gelden per rechtsgrond en naar welke artikelen wordt verwezen?"
)


def test_gdpr_lawful_basis_planner_targets_article_6():
    plan = LegalSourcePlannerService().plan(QUESTION)
    assert plan is not None
    assert plan.plan_id == "gdpr_lawful_basis"
    assert plan.celex == "32016R0679"
    assert "6" in plan.articles


def test_gdpr_lawful_basis_question_is_article_lookup():
    intent = QuestionIntentService().analyze(QUESTION)
    assert intent.requires_rag_pipeline is True
    assert intent.question_type == "article_lookup"
    assert intent.legal_domain == "privacy"


def test_gdpr_lawful_basis_professional_extractive():
    from backend.src.services.legal_extractive_answer_service import LegalExtractiveAnswerService

    chunks = [{
        "celex": "32016R0679",
        "article_number": "6",
        "text": (
            "Artikel 6 Rechtmatigheid van de verwerking 1. De verwerking is slechts rechtmatig "
            "indien en voor zover aan minstens één van de grondslagen van lid 1 is voldaan."
        ),
    }]
    answer = LegalExtractiveAnswerService().build_professional_answer(QUESTION, chunks)
    assert answer
    assert "artikel 6" in answer.lower()
    assert "6(1)(f)" in answer or "Gerechtvaardigd belang" in answer
    assert "Wettelijke grondslag" in answer

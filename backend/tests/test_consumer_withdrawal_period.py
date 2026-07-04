"""Consumer withdrawal period (Richtlijn 2011/83/EU art. 9) regression."""
from backend.src.services.legal_source_planner_service import LegalSourcePlannerService
from backend.src.services.layperson_topic_service import LaypersonTopicService
from backend.src.services.legal_extractive_answer_service import LegalExtractiveAnswerService

QUESTION = (
    "Hoe lang bedraagt de herroepingstermijn voor een overeenkomst op afstand "
    "volgens Richtlijn 2011/83/EU?"
)


def test_withdrawal_planner_not_customs_ucc():
    plan = LegalSourcePlannerService().plan(QUESTION)
    assert plan is not None
    assert plan.plan_id == "consumer_withdrawal"
    assert plan.celex == "32011L0083"
    assert "9" in plan.articles


def test_withdrawal_layperson_topic_matches():
    match = LaypersonTopicService().match(QUESTION)
    assert match is not None
    assert match.topic_id == "consumer_withdrawal_period"


def test_withdrawal_extractive_mentions_14_days():
    chunks = [{
        "celex": "32011L0083",
        "article_number": "9",
        "text": (
            "Artikel 9 Bedenktijd 1. De consument beschikt over een bedenktijd van "
            "14 dagen om zonder opgave van redenen de overeenkomst te herroepen."
        ),
    }]
    answer = LegalExtractiveAnswerService().build_layperson_answer(QUESTION, chunks)
    assert answer
    assert "14" in answer
    assert "herroeping" in answer.lower() or "bedenktijd" in answer.lower()

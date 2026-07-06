"""Tests for layperson answer frame and synoptic composition."""
from backend.src.services.layperson_answer_frame_service import resolve_layperson_answer_frame
from backend.src.services.legal_source_planner_service import LegalSourcePlannerService
from backend.src.utils.layperson_synoptic_composer import compose_synoptic_layperson_answer

EMAIL_Q = "Mag mijn werkgever mijn e-mailadres doorgeven aan een reclamebedrijf?"
RECALL_Q = "Ik heb een webshop met speelgoed. Wanneer moet ik een product terugroepen?"
WITHDRAWAL_Q = "Ik heb online schoenen gekocht maar ze passen niet. Hoe lang mag ik wachten met terugsturen?"


def test_planner_maps_email_marketing_to_gdpr_sharing():
    plan = LegalSourcePlannerService().plan(EMAIL_Q)
    assert plan is not None
    assert plan.plan_id in {"gdpr_marketing_sharing", "gdpr_lawful_basis"}
    assert plan.celex == "32016R0679"
    assert "6" in plan.articles


def test_frame_gives_permission_lead_for_email_question():
    frame = resolve_layperson_answer_frame(EMAIL_Q)
    assert frame is not None
    assert "niet zonder meer" in frame.synoptic_lead.lower()
    assert frame.intent == "permission"


def test_frame_gives_when_lead_for_recall_question():
    frame = resolve_layperson_answer_frame(RECALL_Q)
    assert frame is not None
    assert frame.plan_id == "gpsr_manufacturer_risk"
    assert "onveilig" in frame.synoptic_lead.lower()


def test_frame_gives_deadline_lead_for_withdrawal_question():
    frame = resolve_layperson_answer_frame(WITHDRAWAL_Q)
    assert frame is not None
    assert frame.plan_id == "consumer_withdrawal"
    assert "14 dagen" in frame.synoptic_lead


def test_synoptic_answer_leads_with_direct_answer_not_sanction_text():
    chunks = [
        {
            "celex": "32016R0679",
            "article_number": "6",
            "text": (
                "Artikel 6. Rechtmatigheid van de verwerking 1. De verwerking is alleen rechtmatig "
                "indien en voor zover aan ten minste een van de onderstaande voorwaarden is voldaan: "
                "a) de betrokkene heeft toestemming gegeven voor de verwerking van zijn persoonsgegevens."
            ),
        },
        {
            "celex": "32016R0679",
            "article_number": "21",
            "text": (
                "Artikel 21. Recht van bezwaar 1. De betrokkene heeft het recht om bezwaar te maken "
                "tegen de verwerking van hem betreffende persoonsgegevens met het oog op direct marketing."
            ),
        },
    ]
    frame = resolve_layperson_answer_frame(EMAIL_Q)
    assert frame is not None
    answer = compose_synoptic_layperson_answer(EMAIL_Q, chunks, frame)
    assert answer is not None
    kort = answer.split("## Wat de EU-regels zeggen")[0]
    assert "verbeurdverklaring" not in kort.lower()
    assert "rechtmatig" in kort.lower() or "niet zonder meer" in kort.lower()
    assert "Artikel 6" in answer or "Art. 6" in answer

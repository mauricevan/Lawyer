"""Tests for question intent analysis (system instruction v1.0)."""
from backend.src.services.question_intent_service import QuestionIntentService


def test_customs_declaration_change_is_specific():
    question = (
        "Mag een bedrijf een invoeraangifte wijzigen nadat de goederen zijn vrijgegeven? "
        "Noem de relevante artikelen."
    )
    intent = QuestionIntentService().analyze(question)
    assert intent.requires_rag_pipeline is True
    assert intent.legal_domain == "customs"
    assert intent.question_type == "article_lookup"
    assert intent.suggested_celex == "32013R0952"


def test_ucc_overview_is_generic():
    intent = QuestionIntentService().analyze("Wat regelt Verordening (EU) nr. 952/2013?")
    assert intent.requires_rag_pipeline is False
    assert intent.specificity in {"generic", "general"}


def test_registry_intro_topic_flag():
    service = QuestionIntentService()
    assert service.is_registry_intro_topic("customs_union") is True
    assert service.is_registry_intro_topic("spam_sms") is False

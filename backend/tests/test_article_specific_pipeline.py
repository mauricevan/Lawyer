"""Tests for specific-question pipeline and gap formatting."""
from backend.src.services.answer_specificity_guard_service import AnswerSpecificityGuardService
from backend.src.services.answer_template_bundle_service import AnswerTemplateBundleService
from backend.src.services.insufficient_coverage_answer_service import InsufficientCoverageAnswerService
from backend.src.services.question_intent_service import QuestionIntentService
from backend.src.services.coverage_guidance_service import CoverageGuidanceService
from backend.src.services.topic_intent_gate_service import TopicIntentGateService
from shared.schemas.query import QueryRequest


def test_article_lookup_blocks_registry_intro_topic():
    question = (
        "Mag een bedrijf een invoeraangifte wijzigen nadat de goederen zijn vrijgegeven? "
        "Noem de relevante artikelen."
    )
    request = QueryRequest(question=question, audience="layperson", language="nl")
    intent = QuestionIntentService().analyze(question)
    gate = TopicIntentGateService()
    assert intent.question_type == "article_lookup"
    assert gate.should_block_topic_template(request, intent, "customs_union") is True


def test_layperson_mag_ik_uses_topic_not_gap():
    request = QueryRequest(
        question="Mag ik met mijn Nederlandse rijbewijs in Italië rijden volgens EU-regels?",
        audience="layperson",
        language="nl",
    )
    intent = QuestionIntentService().analyze(request.question)
    gate = TopicIntentGateService()
    parts = AnswerTemplateBundleService().try_topic_template(request)
    assert intent.requires_rag_pipeline is True
    assert parts is not None
    assert gate.should_block_topic_template(request, intent, parts[0].topic_id) is False


def test_layperson_mag_de_deliveroo_topic_allowed():
    request = QueryRequest(
        question="Ik bestelde eten via Deliveroo en werd ziek. Kan ik de verkoper aansprakelijk stellen volgens EU-recht?",
        audience="layperson",
        language="nl",
    )
    intent = QuestionIntentService().analyze(request.question)
    parts = AnswerTemplateBundleService().try_topic_template(request)
    assert parts is not None
    assert TopicIntentGateService().should_block_topic_template(
        request, intent, parts[0].topic_id,
    ) is False


def test_specific_gap_contains_required_phrase():
    question = (
        "Mag een bedrijf een invoeraangifte wijzigen nadat de goederen zijn vrijgegeven? "
        "Noem de relevante artikelen."
    )
    intent = QuestionIntentService().analyze(question)
    guidance = CoverageGuidanceService().resolve(question)
    answer = InsufficientCoverageAnswerService().build(
        guidance, "topic_not_in_corpus", "professional", question, intent,
    )
    assert "kon geen specifieke wettekst worden gevonden" in answer.lower()
    assert "eur-lex" in answer.lower()


def test_layperson_procedural_gap_not_specific_wording():
    question = "Mag ik met mijn Nederlandse rijbewijs in Italië rijden volgens EU-regels?"
    intent = QuestionIntentService().analyze(question)
    guidance = CoverageGuidanceService().resolve(question)
    answer = InsufficientCoverageAnswerService().build(
        guidance, "topic_not_in_corpus", "layperson", question, intent,
    )
    assert "kon geen specifieke wettekst worden gevonden" not in answer.lower()


def test_specificity_guard_blocks_generic_ucc_intro():
    intent = QuestionIntentService().analyze(
        "Mag een bedrijf een invoeraangifte wijzigen nadat de goederen zijn vrijgegeven? "
        "Noem de relevante artikelen.",
    )
    answer = (
        "## Kort antwoord\n"
        "Verordening 952/2013 moderniseert douaneprocessen in de EU.\n\n"
        "## Uitleg\nRaadpleeg TARIC."
    )
    assert AnswerSpecificityGuardService().violates_rules(answer, intent) is True


def test_specificity_guard_allows_legal_basis_table():
    intent = QuestionIntentService().analyze(
        "Mag een bedrijf een invoeraangifte wijzigen nadat de goederen zijn vrijgegeven? "
        "Noem de relevante artikelen.",
    )
    answer = (
        "## Kort antwoord\nNee, niet vrij.\n\n"
        "## Wettelijke grondslag\n| Artikel | Verordening | Wat het regelt |\n"
        "| Art. 164 | UCC | Wijziging na vrijgave |"
    )
    assert AnswerSpecificityGuardService().violates_rules(answer, intent) is False

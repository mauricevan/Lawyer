"""Tests for context adequacy gate."""
from shared.schemas.query import QueryFilters

from backend.src.services.context_adequacy_service import ContextAdequacyService


def test_no_chunks_is_inadequate() -> None:
    service = ContextAdequacyService()
    result = service.assess("Wat is GDPR?", [], retrieval_route="local")
    assert not result.is_adequate
    assert result.reason == "no_chunks"
    assert result.coverage_status == "insufficient"


def test_national_law_question_returns_insufficient_not_crash() -> None:
    service = ContextAdequacyService()
    result = service.assess(
        "Hoeveel vakantiedagen heb ik volgens de Nederlandse wet?",
        [{"text": "irrelevant EU prospectus rules for securities offerings.", "score": 0.5}],
        retrieval_route="local",
    )
    assert not result.is_adequate
    assert result.reason == "topic_not_in_corpus"
    assert result.coverage_status == "insufficient"


def test_standplaatsvergunning_is_national_law_gap() -> None:
    service = ContextAdequacyService()
    result = service.assess(
        "standplaatsvergunning markt nederland",
        [{
            "celex": "32014R0596",
            "text": "Marktmisbruik en transparantie voor marktdeelnemers.",
            "score": 0.9,
            "rerank_score": 0.88,
        }],
        retrieval_route="hybrid",
    )
    assert not result.is_adequate
    assert result.coverage_status == "insufficient"


def test_surveillance_question_with_employment_hours_intent_is_irrelevant() -> None:
    service = ContextAdequacyService()
    question = (
        "Mijn werkgever wil mijn e-mails door AI scannen voor productiviteit. Mag dat?"
    )
    chunks = [
        {
            "title": "Richtlijn arbeidstijden",
            "text": "Werkrooster en rusttijden voor uitzendkrachten.",
            "score": 0.72,
            "rerank_score": 0.68,
        }
    ]
    filters = QueryFilters(intent_id="INT-EMPLOYMENT-HOURS")
    result = service.assess(question, chunks, retrieval_route="local", filters=filters)
    assert not result.is_adequate
    assert result.reason == "irrelevant_retrieval"
    assert result.coverage_status == "irrelevant"


def test_workplace_topic_without_privacy_chunks_is_inadequate() -> None:
    service = ContextAdequacyService()
    question = "Mag mijn werkgever Teams-chats monitoren?"
    chunks = [
        {
            "title": "Prospectusverordening",
            "text": "Openbare aanbieding van effecten.",
            "score": 0.8,
            "rerank_score": 0.75,
        }
    ]
    result = service.assess(question, chunks, retrieval_route="local")
    assert not result.is_adequate
    assert result.reason == "topic_not_in_corpus"


def test_gdpr_chunks_are_adequate_for_privacy_question() -> None:
    service = ContextAdequacyService()
    question = "Mag mijn werkgever mijn persoonsgegevens verwerken?"
    chunks = [
        {
            "title": "GDPR persoonsgegevens",
            "text": "Verwerking van persoonsgegevens en privacy.",
            "score": 0.8,
            "rerank_score": 0.76,
        }
    ]
    result = service.assess(question, chunks, retrieval_route="local")
    assert result.is_adequate


def test_whistleblower_with_hint_celex_chunks_is_adequate() -> None:
    service = ContextAdequacyService()
    question = (
        "Wat verplicht de EU-whistleblower-richtlijn werkgevers te doen bij meldingen?"
    )
    chunks = [{
        "celex": "32024L1385",
        "title": "Whistleblower richtlijn",
        "text": "Artikel 5 Intern meldkanaal voor meldingen van inbreuken door werkgevers.",
        "score": 0.9,
        "rerank_score": 0.85,
    }]
    result = service.assess(question, chunks, retrieval_route="live_fallback")
    assert result.is_adequate


def test_whatsapp_workplace_not_blocked_when_avg_chunks_present() -> None:
    service = ContextAdequacyService()
    question = "Mag mijn werkgever mijn WhatsApp-berichten lezen?"
    chunks = [{
        "celex": "32016R0679",
        "title": "AVG",
        "text": "Verwerking van persoonsgegevens en privacy op het werk.",
        "score": 0.85,
        "rerank_score": 0.8,
    }]
    result = service.assess(question, chunks, retrieval_route="hybrid")
    assert result.is_adequate


def test_professional_high_risk_without_matching_chunks_is_inadequate() -> None:
    service = ContextAdequacyService()
    question = "Welke verplichtingen gelden voor high-risk AI systemen?"
    chunks = [
        {
            "title": "Prospectusverordening",
            "text": "Openbare aanbieding van effecten.",
            "score": 0.7,
            "rerank_score": 0.66,
        }
    ]
    result = service.assess(question, chunks, retrieval_route="local", audience="professional")
    assert not result.is_adequate

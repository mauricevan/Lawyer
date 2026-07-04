"""Tests for answer policy enforcement."""
from shared.schemas.citation import Citation

from backend.src.services.answer_policy_service import AnswerPolicyService


def test_enforce_citations_builds_from_chunks_when_empty() -> None:
    policy = AnswerPolicyService()
    chunks = [{"celex": "32022R2065", "article_number": "5", "text": "DORA tekst", "title": "DORA"}]
    citations = policy.enforce_citations([], chunks)
    assert len(citations) == 1
    assert citations[0].celex == "32022R2065"


def test_enforce_citations_keeps_existing() -> None:
    policy = AnswerPolicyService()
    existing = [Citation(celex="32022R2065", excerpt="x", eurlex_url="https://example.com")]
    chunks = [{"celex": "32022R2065", "text": "y"}]
    citations = policy.enforce_citations(existing, chunks)
    assert citations == existing


def test_finalize_adds_localized_disclaimer() -> None:
    policy = AnswerPolicyService()
    _, _, disclaimer = policy.finalize_answer("Réponse.", [], [], "layperson", "fr")
    assert "avocat" in disclaimer.lower()


def test_finalize_adds_disclaimer_and_insufficient_notice() -> None:
    policy = AnswerPolicyService()
    answer, citations, disclaimer = policy.finalize_answer(
        "Kort antwoord zonder bron.",
        [],
        [],
        "layperson",
    )
    assert "advocaat" in disclaimer.lower() or "juridisch" in disclaimer.lower()
    assert "Let op" in answer
    assert citations == []


def test_finalize_strips_artikel_none_from_answer() -> None:
    policy = AnswerPolicyService()
    answer, _, _ = policy.finalize_answer(
        "Registratie volgens artikel None is vereist.",
        [],
        [{"celex": "32024R1689", "text": "AI Act"}],
        "layperson",
    )
    assert "none" not in answer.lower()

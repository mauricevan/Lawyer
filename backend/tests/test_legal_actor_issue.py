"""Tests for legal actor/issue interpretation and chunk scoring."""
from backend.src.utils.legal_actor_issue_chunk_scoring import (
    rank_chunks_by_legal_context,
    score_chunk_for_context,
)
from backend.src.utils.legal_question_interpretation import infer_legal_context
from backend.src.utils.layperson_actor_gate import is_wrong_actor_answer

CE_QUESTION = (
    "Wanneer mag een fabrikant een product op de markt brengen zonder CE-markering?"
)
SURVEILLANCE_CHUNK = {
    "text": (
        "Market surveillance authorities shall take appropriate measures if a product "
        "subject to Union harmonisation legislation does not conform."
    ),
}
MANUFACTURER_CHUNK = {
    "text": (
        "De fabrikant brengt alleen producten op de markt die voldoen aan de "
        "toepasselijke harmonisatiewetgeving en CE-markering waar verplicht."
    ),
}


def test_infer_manufacturer_market_access():
    actor, issue = infer_legal_context(CE_QUESTION)
    assert actor == "manufacturer"
    assert issue == "market_access"


def test_infer_consumer_obligation():
    actor, issue = infer_legal_context("Welke verplichtingen heeft een consument bij online aankoop?")
    assert actor == "consumer"
    assert issue == "obligation"


def test_surveillance_chunk_penalized_for_manufacturer_access():
    score = score_chunk_for_context(
        SURVEILLANCE_CHUNK["text"], "manufacturer", "market_access",
    )
    assert score < 0


def test_manufacturer_chunk_ranked_above_surveillance():
    ranked = rank_chunks_by_legal_context(
        [SURVEILLANCE_CHUNK, MANUFACTURER_CHUNK],
        "manufacturer",
        "market_access",
    )
    assert ranked[0] is MANUFACTURER_CHUNK


def test_rights_chunk_scored_for_rights_issue():
    text = "Workers have the right to equal treatment without discrimination on grounds of disability."
    score = score_chunk_for_context(text, "employee", "rights")
    assert score >= 2


def test_wrong_actor_answer_detects_surveillance_dump():
    answer = (
        "## Kort antwoord\n"
        "Voor fabrikanten gelden onder meer deze verplichtingen: Market surveillance "
        "authorities shall take appropriate measures.\n\n"
        "## Uitleg\nMarket surveillance authorities shall take appropriate measures."
    )
    assert is_wrong_actor_answer(answer, "manufacturer", "market_access")


def test_legal_dump_start_triggers_retry():
    answer = (
        "## Kort antwoord\n"
        "This Directive shall apply to all products placed on the market.\n\n"
        "## Uitleg\nMeer uitleg."
    )
    assert is_wrong_actor_answer(answer, "manufacturer", "market_access")

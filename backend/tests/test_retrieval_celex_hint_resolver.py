"""Unit tests for CELEX hint resolution in live fallback."""
from backend.src.utils.celex_hint_resolver import (
    cached_chunks_are_usable,
    chunks_include_celex,
    resolve_live_celex_hint,
    should_force_hint_live_fallback,
)
from shared.schemas.query import QueryFilters

HORSE_QUESTION = (
    "Als ik een paard van zuiver ras importeer onder goederen code 0101 - "
    "is de kans dan groot dat deze goederencode juist is?"
)


def test_resolve_live_celex_hint_for_classification_question():
    assert resolve_live_celex_hint(HORSE_QUESTION, None, None) == "31987R2658"


def test_resolve_live_celex_hint_prefers_filter_celex():
    filters = QueryFilters(celex="32016R0679")
    assert resolve_live_celex_hint(HORSE_QUESTION, filters, None) == "32016R0679"


def test_resolve_live_celex_hint_uses_planner_for_customs_refund():
    question = "Kan de importeur terugbetaling van invoerrechten krijgen na douanewaarde correctie?"
    assert resolve_live_celex_hint(question, None, None) == "32013R0952"


def test_resolve_live_celex_hint_prefers_oj_override():
    assert resolve_live_celex_hint(HORSE_QUESTION, None, "32013R0952") == "32013R0952"


def test_should_force_when_hint_index_empty():
    assert should_force_hint_live_fallback([], [], "31987R2658")


def test_should_force_when_reranked_missing_hint_celex():
    reranked = [{"celex": "32016R0679", "score": 0.45}]
    assert should_force_hint_live_fallback([], reranked, "31987R2658")


def test_should_not_force_when_reranked_has_hint_celex():
    reranked = [{
        "celex": "31987R2658",
        "score": 0.9,
        "text": "0101 Paarden levend. 0101 21 00 Fokdieren van zuiver ras voor import en douane.",
    }]
    hint_hits = [{
        "celex": "31987R2658",
        "chunk_id": "local:1",
        "score": 0.9,
        "text": "0101 Paarden levend. 0101 21 00 Fokdieren van zuiver ras voor import en douane.",
    }]
    assert not should_force_hint_live_fallback(hint_hits, reranked, "31987R2658")


def test_should_not_force_when_usable_indexed_chunks_exist():
    hint_hits = [{
        "celex": "31987R2658",
        "chunk_id": "local:1",
        "text": (
            "0101 Paarden levend. 0101 21 00 Fokdieren van zuiver ras voor import. "
            "Douane en tariefindeling volgens de gecombineerde nomenclatuur."
        ) * 4,
    }]
    reranked = [{"celex": "32016R0679", "score": 0.45, "text": "GDPR personal data rules " * 10}]
    assert not should_force_hint_live_fallback(hint_hits, reranked, "31987R2658")


def test_chunks_include_celex():
    chunks = [{"celex": "31987R2658"}]
    assert chunks_include_celex(chunks, "31987R2658")
    assert not chunks_include_celex(chunks, "32016R0679")


def test_cached_chunks_invalid_when_hint_celex_missing():
    gdpr_chunks = [{
        "celex": "32016R0679",
        "score": 0.9,
        "text": "Artikel 6 GDPR lawful basis for processing personal data in employment context.",
    }]
    assert not cached_chunks_are_usable(gdpr_chunks, "32024L1385")

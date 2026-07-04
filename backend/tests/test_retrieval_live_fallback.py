"""Tests for forced live fallback when local index is empty."""
import pytest

from backend.src.utils.retrieval_live_fallback import should_force_live_despite_budget, try_live_fallback
from backend.src.utils.retrieval_budget import RetrievalBudget
from shared.schemas.query import QueryRequest


def test_should_force_live_when_celex_hint_and_no_local_chunks():
    assert should_force_live_despite_budget("32016R0679", [], []) is True
    assert should_force_live_despite_budget(None, [], []) is False
    assert should_force_live_despite_budget(
        "32016R0679",
        [],
        [{"celex": "32016R0679", "text": "x" * 120, "score": 0.9}],
    ) is False


class _FakeLive:
    async def fallback_chunks(self, question, language="nl", celex_hint=None, is_celex_allowed=None):
        return [{
            "chunk_id": "live:32016R0679_6",
            "celex": "32016R0679",
            "article": "6",
            "text": "Artikel 6 Rechtmatigheid van de verwerking. De verwerking is slechts rechtmatig indien en voor zover aan minstens één van de grondslagen van lid 1 is voldaan.",
            "source": "live_fallback",
        }]


class _FakeCache:
    def __init__(self) -> None:
        self.stored: list[dict] = []

    async def set(self, cache_key, chunks, question):
        self.stored = list(chunks)


class _FakeFlags:
    def is_live_fallback_enabled(self) -> bool:
        return True


class _FakeDeprecation:
    def is_celex_allowed(self, celex, allowed_lang, filters):
        return True

    def filter_chunks(self, chunks, filters):
        return chunks


@pytest.mark.asyncio
async def test_try_live_fallback_forces_despite_exhausted_budget():
    question = (
        "Op welke rechtsgronden kan een organisatie persoonsgegevens verwerken "
        "zonder toestemming volgens de AVG?"
    )
    request = QueryRequest(question=question, audience="professional", language="nl")
    budget = RetrievalBudget(0.0)
    cache = _FakeCache()
    chunks, route = await try_live_fallback(
        request,
        budget,
        "cache-key",
        "nl",
        None,
        [],
        [],
        [],
        _FakeLive(),
        cache,
        _FakeDeprecation(),
        _FakeFlags(),
        celex_hint_override="32016R0679",
    )
    assert route == "live_fallback"
    assert chunks
    assert chunks[0]["celex"] == "32016R0679"
    assert cache.stored

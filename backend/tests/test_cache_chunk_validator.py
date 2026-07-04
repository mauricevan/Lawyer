"""Tests for cache chunk validation."""
from backend.src.utils.cache_chunk_validator import filter_cacheable_chunks, is_cacheable_chunk


def test_rejects_misschien_in_chunk_text() -> None:
    chunk = {
        "celex": "32024R1689",
        "text": "Misschien geldt registratie voor chatbots onder de AI Act.",
    }
    assert not is_cacheable_chunk(chunk)


def test_accepts_valid_chunk() -> None:
    chunk = {
        "celex": "32024R1689",
        "text": "Transparantieverplichtingen voor AI-systemen en chatbots in de EU.",
    }
    assert is_cacheable_chunk(chunk)


def test_rejects_irrelevant_live_fallback_for_chatbot_question() -> None:
    chunk = {
        "celex": "32003L0088",
        "title": "Richtlijn arbeidstijden",
        "text": "Rusttijden en werkroosters voor uitzendkrachten in de Europese Unie.",
        "source": "live_fallback",
    }
    question = "Moet ik mijn chatbot registreren bij de overheid?"
    assert not is_cacheable_chunk(chunk, question)


def test_filter_cacheable_chunks() -> None:
    chunks = [
        {"celex": "32024R1689", "text": "AI Act transparantie voor chatbots en systemen."},
        {"celex": "32003L0088", "text": "Misschien arbeidstijden."},
    ]
    filtered = filter_cacheable_chunks(chunks)
    assert len(filtered) == 1
    assert filtered[0]["celex"] == "32024R1689"

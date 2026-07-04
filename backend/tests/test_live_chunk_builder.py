"""Tests for ingestion-based live chunk builder."""
from backend.src.services.live_chunk_builder import LiveChunkBuilder

SAMPLE_HTML = b"""
<html><body>
<h2>Article 1</h2>
<p>This regulation establishes digital operational resilience requirements for financial entities.</p>
<h2>Article 2</h2>
<p>Financial entities shall maintain ICT risk management frameworks with documented policies.</p>
</body></html>
"""


def test_build_from_html_creates_structured_chunks():
    builder = LiveChunkBuilder()
    chunks = builder.build_from_html("32022R2554", SAMPLE_HTML, "en", "DORA", None)
    assert chunks
    assert chunks[0]["celex"] == "32022R2554"
    assert "operational resilience" in chunks[0]["text"].lower()
    assert chunks[0]["source"] == "live_fallback"


CLASSIFICATION_HTML = b"""
<html><body>
<p>Hoofdstuk 1 Levende dieren.</p>
<p>0101 Paarden, ezels, muilezels en hetzelven, levend.</p>
<p>0101 21 00 Fokdieren van zuiver ras.</p>
<p>0101 29 Andere paarden.</p>
<p>0102 Rundvee levend.</p>
</body></html>
"""


def test_classification_question_ranks_cn_code_chunks_first():
    builder = LiveChunkBuilder()
    question = (
        "Als ik een paard van zuiver ras importeer onder goederen code 0101 - "
        "is de kans dan groot dat deze goederencode juist is?"
    )
    chunks = builder.build_from_html(
        "31987R2658", CLASSIFICATION_HTML, "nl", "GN", None, question=question,
    )
    assert chunks
    combined = " ".join(chunk["text"].lower() for chunk in chunks)
    assert "0101" in combined
    assert "paard" in combined


def test_strict_articles_returns_empty_when_no_match():
    builder = LiveChunkBuilder()
    chunks = builder.build_from_html(
        "32022R2554",
        SAMPLE_HTML,
        "en",
        "DORA",
        None,
        article_hints=("99",),
        strict_articles=True,
    )
    assert chunks == []


def test_keyword_rank_selects_relevant_chunks():
    builder = LiveChunkBuilder()
    chunks = builder.build_from_html(
        "32022R2554",
        SAMPLE_HTML,
        "en",
        "DORA",
        None,
        search_keywords=("ICT risk",),
        agent_mode=True,
    )
    assert chunks
    assert "ict" in chunks[0]["text"].lower()

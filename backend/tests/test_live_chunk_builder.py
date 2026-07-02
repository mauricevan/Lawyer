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

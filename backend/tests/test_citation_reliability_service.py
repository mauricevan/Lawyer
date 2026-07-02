"""Tests for citation reliability counters."""
from backend.src.services.citation_reliability_service import CitationReliabilityService


def test_snapshot_tracks_coverage() -> None:
    service = CitationReliabilityService()
    service.record(citation_count=2, confidence=0.7, route="local")
    service.record(citation_count=0, confidence=0.1, route="live_fallback")
    snapshot = service.snapshot()
    assert snapshot["query_total"] == 2
    assert snapshot["citation_coverage_rate"] == 0.5
    assert snapshot["low_confidence_rate"] == 0.5

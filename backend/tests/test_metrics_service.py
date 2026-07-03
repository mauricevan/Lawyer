"""Unit tests for readiness metrics counters (plan14 AA)."""
from backend.src.services.metrics_service import MetricsService


def test_readiness_pass_rate_tracks_checks():
    metrics = MetricsService()
    metrics.record_readiness_check(True)
    metrics.record_readiness_check(True)
    metrics.record_readiness_check(False)
    snapshot = metrics.readiness_snapshot()
    assert snapshot["checks_total"] == 3
    assert snapshot["checks_passed"] == 2
    assert snapshot["pass_rate"] == round(2 / 3, 4)

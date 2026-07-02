"""Tests for Prometheus metrics exposition."""
from backend.src.services.metrics_service import metrics_service
from backend.src.services.prometheus_exporter import export_prometheus


def test_prometheus_export_contains_registered_metrics():
    metrics_service.record_query(is_stream=False)
    metrics_service.record_cache_hit()
    payload, content_type = export_prometheus()
    assert content_type.startswith("text/plain")
    if payload:
        assert b"lawyer_queries_total" in payload
        assert b"lawyer_cache_hits_total" in payload

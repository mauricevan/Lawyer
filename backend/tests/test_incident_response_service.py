"""Unit tests for tier-1 alert runbook coverage (plan14 AD)."""
from pathlib import Path

from backend.src.services.incident_response_service import IncidentResponseService


def test_incident_playbook_audit_passes():
    report = IncidentResponseService().audit()
    assert report["passed"], report["issues"]


def test_tier1_alert_runbook_coverage_is_complete():
    coverage = IncidentResponseService().build_coverage()
    assert coverage["coverage_ratio"] == 1.0
    assert coverage["linked_count"] == coverage["tier1_alert_count"]


def test_summarize_admin_exposes_coverage_metric():
    service = IncidentResponseService()
    summary = service.summarize_admin()
    assert summary["coverage_ratio"] == 1.0
    assert summary["tier1_alert_count"] >= 4
    assert summary["unlinked_alerts"] == []


def test_prometheus_alerts_include_runbook_urls():
    repo = Path(__file__).resolve().parents[2]
    indexed = IncidentResponseService(root=repo).audit()["coverage"]["alerts"]
    assert len(indexed) >= 4
    for row in indexed:
        assert row["prometheus_runbook_url"]

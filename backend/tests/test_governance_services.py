"""Tests for plan15 governance services (AB-AD)."""
from backend.src.services.decision_log_service import DecisionLogService
from backend.src.services.governance_report_service import GovernanceReportService
from backend.src.services.risk_acceptance_service import RiskAcceptanceService


def test_risk_acceptance_gate_passes():
    assert RiskAcceptanceService().audit()["passed"]


def test_decision_log_audit_passes():
    assert DecisionLogService().audit()["passed"]


def test_governance_snapshot_passes():
    assert GovernanceReportService().audit()["passed"]

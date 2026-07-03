"""Unit tests for readiness pass-rate gate (plan14 KPI)."""
from backend.src.services.readiness_gate_service import ReadinessGateService


def test_readiness_pass_rate_gate_passes_at_99_percent():
    service = ReadinessGateService()
    report = service.evaluate_samples([True, True, True, False], "test")
    assert report["pass_rate"] == 0.75
    assert report["passed"] is False


def test_readiness_pass_rate_gate_passes_when_all_ok():
    service = ReadinessGateService()
    report = service.simulate_report()
    assert report["passed"] is True
    assert report["pass_rate"] >= 0.99


def test_readiness_pass_rate_requires_min_samples():
    service = ReadinessGateService()
    report = service.evaluate_samples([True], "test")
    assert report["passed"] is False
    assert any("min_samples" in item for item in report["violations"])

"""Tests for input validation audit registry."""
from backend.src.security.input_validation_audit import build_coverage_report, run_audit


def test_validation_coverage_is_complete() -> None:
    report = build_coverage_report()
    assert report["coverage_percent"] == 100.0
    assert report["gaps"] == []


def test_run_audit_passes() -> None:
    report = run_audit(min_coverage=100.0)
    assert report["validated_endpoints"] == report["total_endpoints"]

"""Unit tests for recovery drill MTTR and gates (plan14 AC)."""
from datetime import datetime, timedelta, timezone
from pathlib import Path

import json

from backend.src.services.recovery_drill_service import DrillPhase, RecoveryDrillService


def _phase(name: str, seconds: float, passed: bool = True) -> DrillPhase:
    now = datetime.now(timezone.utc).isoformat()
    return DrillPhase(name, now, now, seconds, passed)


def test_recovery_drill_mttr_sums_mitigation_and_verify():
    service = RecoveryDrillService()
    phases = [
        _phase("baseline_health", 2.0),
        _phase("mitigation", 30.0),
        _phase("recovery_verify", 10.0),
    ]
    report = service.build_report(phases, "simulate")
    assert report["mttr_seconds"] == 40.0
    assert report["passed"] is True


def test_recovery_drill_gate_fails_when_mttr_exceeds_limit():
    service = RecoveryDrillService()
    phases = [
        _phase("mitigation", 4000.0),
        _phase("recovery_verify", 10.0, passed=True),
    ]
    report = service.build_report(phases, "live")
    assert report["passed"] is False
    assert report["gate"]["passed"] is False


def test_recovery_drill_simulate_phases_pass_gate():
    service = RecoveryDrillService()
    report = service.build_report(service.simulate_phases(), "simulate")
    assert report["passed"] is True
    assert report["mttr_minutes"] < 60


def test_recovery_drill_report_age_gate(tmp_path: Path):
    service = RecoveryDrillService()
    report_path = tmp_path / "recovery.json"
    stale = {
        "completed_at": (datetime.now(timezone.utc) - timedelta(days=120)).isoformat(),
        "passed": True,
        "mttr_minutes": 5,
    }
    report_path.write_text(json.dumps(stale), encoding="utf-8")
    age = service.evaluate_report_age(report_path)
    assert age["passed"] is False
    assert age["age_days"] >= 120

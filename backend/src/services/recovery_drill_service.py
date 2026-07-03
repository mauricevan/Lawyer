"""Recovery drill timing, MTTR, and gate evaluation (plan14 AC)."""
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from backend.src.utils.recovery_drill_config import load_recovery_drill_policy


@dataclass(slots=True)
class DrillPhase:
    name: str
    started_at: str
    ended_at: str
    duration_seconds: float
    passed: bool
    detail: str = ""


class RecoveryDrillService:
    """Builds recovery drill reports and evaluates MTTR gates."""

    def __init__(self) -> None:
        self._policy = load_recovery_drill_policy()

    def build_report(self, phases: list[DrillPhase], mode: str) -> dict[str, Any]:
        mttr_seconds = self._mitigation_mttr_seconds(phases)
        passed = self._all_required_passed(phases) and self._mttr_within_limit(mttr_seconds)
        return {
            "suite": "recovery_drill",
            "mode": mode,
            "passed": passed,
            "mttr_seconds": mttr_seconds,
            "mttr_minutes": round(mttr_seconds / 60, 2),
            "phases": [self._phase_dict(phase) for phase in phases],
            "gate": self.evaluate_gate(mttr_seconds, passed),
            "completed_at": datetime.now(timezone.utc).isoformat(),
        }

    def evaluate_gate(self, mttr_seconds: float, passed: bool) -> dict[str, Any]:
        gate = self._policy.get("gate", {})
        max_mttr = float(gate.get("max_mttr_minutes", 60)) * 60
        violations: list[str] = []
        if mttr_seconds > max_mttr:
            violations.append(f"mttr {mttr_seconds}s exceeds {max_mttr}s")
        if not passed:
            violations.append("one or more drill phases failed")
        return {
            "max_mttr_minutes": gate.get("max_mttr_minutes", 60),
            "passed": not violations,
            "violations": violations,
        }

    def evaluate_report_age(self, report_path: Path) -> dict[str, Any]:
        gate = self._policy.get("gate", {})
        max_age = int(gate.get("max_report_age_days", 92))
        if not report_path.is_file():
            return {"passed": False, "reason": "missing_report", "max_report_age_days": max_age}
        payload = self._load_report(report_path)
        completed = datetime.fromisoformat(payload["completed_at"])
        if completed.tzinfo is None:
            completed = completed.replace(tzinfo=timezone.utc)
        age_days = (datetime.now(timezone.utc) - completed).days
        passed = age_days <= max_age and bool(payload.get("passed"))
        return {
            "passed": passed,
            "age_days": age_days,
            "max_report_age_days": max_age,
            "last_mttr_minutes": payload.get("mttr_minutes"),
        }

    def simulate_phases(self) -> list[DrillPhase]:
        now = datetime.now(timezone.utc)
        mttr = float(self._policy.get("simulate", {}).get("mttr_seconds", 45))
        start = now.isoformat()
        end = now.isoformat()
        return [
            DrillPhase("baseline_health", start, end, 1.0, True),
            DrillPhase("mitigation", start, end, mttr - 5, True, "feature rollback"),
            DrillPhase("recovery_verify", start, end, 4.0, True, "health + ready"),
        ]

    def _mitigation_mttr_seconds(self, phases: list[DrillPhase]) -> float:
        mitigation = self._phase_by_name(phases, "mitigation")
        recovery = self._phase_by_name(phases, "recovery_verify")
        if mitigation and recovery:
            return mitigation.duration_seconds + recovery.duration_seconds
        return sum(phase.duration_seconds for phase in phases)

    def _all_required_passed(self, phases: list[DrillPhase]) -> bool:
        required = {"mitigation", "recovery_verify"}
        named = {phase.name: phase for phase in phases}
        return all(named[name].passed for name in required if name in named)

    def _mttr_within_limit(self, mttr_seconds: float) -> bool:
        gate = self._policy.get("gate", {})
        return mttr_seconds <= float(gate.get("max_mttr_minutes", 60)) * 60

    @staticmethod
    def _phase_by_name(phases: list[DrillPhase], name: str) -> DrillPhase | None:
        for phase in phases:
            if phase.name == name:
                return phase
        return None

    @staticmethod
    def _phase_dict(phase: DrillPhase) -> dict[str, Any]:
        return {
            "name": phase.name,
            "started_at": phase.started_at,
            "ended_at": phase.ended_at,
            "duration_seconds": phase.duration_seconds,
            "passed": phase.passed,
            "detail": phase.detail,
        }

    @staticmethod
    def _load_report(report_path: Path) -> dict[str, Any]:
        import json

        return json.loads(report_path.read_text(encoding="utf-8"))

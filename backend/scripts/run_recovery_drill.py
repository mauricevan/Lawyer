#!/usr/bin/env python3
"""Automated recovery drill with MTTR reporting (plan14 AC)."""
import argparse
import json
import os
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

from backend.src.services.recovery_drill_service import DrillPhase, RecoveryDrillService
from backend.src.utils.recovery_drill_config import recovery_drill_report_path

_REPO = Path(__file__).resolve().parents[2]


def _iso_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _run_command(command: list[str], allow_fail: bool = False) -> tuple[bool, str]:
    result = subprocess.run(command, cwd=_REPO, capture_output=True, text=True)
    output = (result.stdout or result.stderr or "").strip()
    if result.returncode != 0 and not allow_fail:
        return False, output or f"exit {result.returncode}"
    return True, output


def _phase(name: str, runner, detail: str = "") -> DrillPhase:
    started = time.monotonic()
    started_at = _iso_now()
    passed, output = runner()
    ended_at = _iso_now()
    return DrillPhase(
        name=name,
        started_at=started_at,
        ended_at=ended_at,
        duration_seconds=round(time.monotonic() - started, 2),
        passed=passed,
        detail=output or detail,
    )


def _live_phases() -> list[DrillPhase]:
    hotfix = _REPO / "scripts/ops/run-hotfix-rollback.sh"
    rollback = _REPO / "scripts/ops/rollback-features.sh"
    phases = [
        _phase(
            "baseline_health",
            lambda: _run_command([str(hotfix), "--verify-only"], allow_fail=True),
            "pre-drill health",
        ),
        _phase(
            "mitigation",
            lambda: _run_command([str(rollback)]),
            "feature rollback",
        ),
    ]
    if subprocess.run(["docker", "compose", "ps", "-q", "backend"], cwd=_REPO, capture_output=True).stdout.strip():
        _run_command(
            ["docker", "compose", "-f", "docker-compose.yml", "-f", "docker-compose.local.yml", "restart", "backend"],
            allow_fail=True,
        )
        time.sleep(5)
    phases.append(
        _phase(
            "recovery_verify",
            lambda: _run_command([str(hotfix), "--verify-only"]),
            "post-mitigation health",
        )
    )
    return phases


def _write_report(payload: dict, report_path: Path) -> None:
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def run_drill(mode: str) -> dict:
    service = RecoveryDrillService()
    phases = service.simulate_phases() if mode == "simulate" else _live_phases()
    return service.build_report(phases, mode)


def run_gate() -> dict:
    service = RecoveryDrillService()
    report_path = _REPO / recovery_drill_report_path()
    backend_url = os.getenv("BACKEND_URL", "http://127.0.0.1:8001")
    if os.getenv("CI") == "true":
        payload = run_drill("simulate")
        _write_report(payload, report_path)
    elif subprocess.run(["curl", "-sf", f"{backend_url}/health"], capture_output=True).returncode == 0:
        payload = run_drill("live")
        _write_report(payload, report_path)
    elif report_path.is_file():
        age = service.evaluate_report_age(report_path)
        return {"suite": "recovery_drill_gate", "passed": age["passed"], "report_age": age}
    else:
        payload = run_drill("simulate")
        _write_report(payload, report_path)
    age = service.evaluate_report_age(report_path)
    passed = bool(payload.get("passed")) and age["passed"]
    return {"suite": "recovery_drill_gate", "passed": passed, "drill": payload, "report_age": age}


def main() -> None:
    parser = argparse.ArgumentParser(description="Recovery drill automation")
    parser.add_argument("--simulate", action="store_true")
    parser.add_argument("--gate", action="store_true")
    parser.add_argument("--report", type=Path, default=None)
    args = parser.parse_args()
    report_path = args.report or (_REPO / recovery_drill_report_path())
    if args.gate:
        payload = run_gate()
    else:
        mode = "simulate" if args.simulate else "live"
        payload = run_drill(mode)
        _write_report(payload, report_path)
    print(json.dumps(payload, indent=2))
    if not payload.get("passed"):
        raise SystemExit("Recovery drill gate failed")


if __name__ == "__main__":
    main()

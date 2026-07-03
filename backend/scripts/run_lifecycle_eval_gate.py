#!/usr/bin/env python3
"""Lifecycle eval gate for release checklist (plan13 AD)."""
import asyncio
import json
import os
import subprocess
import sys
from pathlib import Path

from backend.src.database import SessionLocal
from backend.src.services.document_lifecycle_metrics_service import DocumentLifecycleMetricsService
from backend.src.services.document_version_conflict_service import DocumentVersionConflictService

_REPO = Path(__file__).resolve().parents[2]


def _run_script(relative_path: str) -> bool:
    script = _REPO / relative_path
    result = subprocess.run(
        [sys.executable, str(script)],
        cwd=_REPO,
        env={**os.environ, "PYTHONPATH": "."},
        capture_output=True,
        text=True,
    )
    if result.stdout.strip():
        print(result.stdout.strip())
    return result.returncode == 0


def _run_deprecation_check() -> dict:
    passed = _run_script("backend/scripts/validate_deprecation_register.py")
    return {"name": "deprecation_register", "passed": passed}


def _run_version_registration_check() -> dict:
    result = DocumentVersionConflictService().validate_registered_families()
    return {"name": "version_registration", "passed": result["passed"], "detail": result}


async def _run_staleness_check() -> dict:
    if not os.getenv("DATABASE_URL"):
        return {"name": "staleness", "passed": True, "skipped": True}
    service = DocumentLifecycleMetricsService()
    async with SessionLocal() as session:
        summary = await service.build_summary(session)
    passed = bool(summary["gate"]["passed"])
    return {"name": "staleness", "passed": passed, "detail": summary["gate"]}


async def run_gate() -> dict:
    checks = [_run_deprecation_check(), _run_version_registration_check(), await _run_staleness_check()]
    return {
        "suite": "lifecycle_eval_gate",
        "passed": all(check["passed"] for check in checks),
        "checks": checks,
    }


def main() -> None:
    payload = asyncio.run(run_gate())
    print(json.dumps(payload, indent=2))
    if not payload["passed"]:
        raise SystemExit("Lifecycle eval gate failed")


if __name__ == "__main__":
    main()

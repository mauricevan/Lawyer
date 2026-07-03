"""Project completion status from gate reports (plan31 AC)."""
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

_REPO = Path(__file__).resolve().parents[3]

_REPORT_PATHS = [
    "docs/data/governance-reports/policy-registry-latest.json",
    "docs/data/governance-reports/partner-api-latest.json",
    "docs/data/reliability-reports/failover-latest.json",
    "docs/data/governance-reports/cycle-plans-latest.json",
    "docs/data/governance-reports/governance-snapshot-latest.json",
]


class ProjectCompletionService:
    """Evaluates production readiness from persisted gate reports."""

    def __init__(self, root: Path | None = None) -> None:
        self._root = root or _REPO

    def audit(self) -> dict[str, Any]:
        gates = [self._load_gate_report(rel) for rel in _REPORT_PATHS]
        scripts_ok = self._scripts_exist()
        passed = scripts_ok and all(row["passed"] for row in gates)
        return {
            "suite": "project_completion",
            "passed": passed,
            "scripts_ok": scripts_ok,
            "gates": gates,
            "completed_at": datetime.now(timezone.utc).isoformat(),
        }

    def summarize_admin(self) -> dict[str, Any]:
        report = self.audit()
        return {
            "production_ready": report["passed"],
            "gates_passed": sum(1 for row in report["gates"] if row["passed"]),
            "gates_total": len(report["gates"]),
        }

    def _scripts_exist(self) -> bool:
        required = [
            "scripts/ops/run-project-completion-gate.sh",
            "scripts/platform/run-partner-api-gate.sh",
            "scripts/platform/run-cycle-plan-gate.sh",
        ]
        return all((self._root / rel).is_file() for rel in required)

    def _load_gate_report(self, rel: str) -> dict[str, Any]:
        path = self._root / rel
        if not path.is_file():
            return {"report": rel, "passed": False, "reason": "missing"}
        payload = json.loads(path.read_text(encoding="utf-8"))
        passed = bool(payload.get("passed"))
        return {"report": rel, "passed": passed, "suite": payload.get("suite")}

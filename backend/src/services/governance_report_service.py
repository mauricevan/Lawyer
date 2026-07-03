"""Governance reporting aggregation (plan15 AD)."""
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import json

from backend.src.services.decision_log_service import DecisionLogService
from backend.src.services.incident_response_service import IncidentResponseService
from backend.src.services.policy_registry_service import PolicyRegistryService
from backend.src.services.risk_acceptance_service import RiskAcceptanceService
from backend.src.utils.governance_report_config import load_governance_report_policy, repo_root


class GovernanceReportService:
    """Builds governance snapshot for admin and quarterly ops."""

    def __init__(self, root: Path | None = None) -> None:
        self._root = root or repo_root()
        self._policy = load_governance_report_policy()

    def build_snapshot(self) -> dict[str, Any]:
        return {
            "suite": "governance_snapshot",
            "completed_at": datetime.now(timezone.utc).isoformat(),
            "policy_registry": PolicyRegistryService(self._root).summarize_admin(),
            "risk_acceptance": RiskAcceptanceService(self._root).summarize_admin(),
            "decision_log": DecisionLogService(self._root).summarize_admin(),
            "incident_response": IncidentResponseService(self._root).summarize_admin(),
        }

    def audit(self) -> dict[str, Any]:
        snapshot = self.build_snapshot()
        gate = self._policy.get("gate", {})
        min_sections = int(gate.get("min_sections", 4))
        present = [key for key in self._policy.get("sections", []) if key in snapshot]
        passed = len(present) >= min_sections
        return {
            "suite": "governance_snapshot",
            "passed": passed,
            "snapshot": snapshot,
            "gate": {"min_sections": min_sections, "passed": passed},
        }

    def summarize_admin(self) -> dict[str, Any]:
        snapshot = self.build_snapshot()
        report_path = self._root / str(self._policy.get("report", {}).get("path", ""))
        age_days = self._report_age_days(report_path)
        gate = self._policy.get("gate", {})
        fresh = age_days <= int(gate.get("max_report_age_days", 7)) if report_path.is_file() else False
        return {**snapshot, "report_fresh": fresh, "report_age_days": age_days}

    def write_report(self, payload: dict[str, Any] | None = None) -> Path:
        data = payload or self.audit()
        rel = str(self._policy.get("report", {}).get("path", "docs/data/governance-reports/governance-snapshot-latest.json"))
        path = self._root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
        return path

    def _report_age_days(self, path: Path) -> int:
        if not path.is_file():
            return 999
        payload = json.loads(path.read_text(encoding="utf-8"))
        completed = datetime.fromisoformat(payload["snapshot"]["completed_at"])
        if completed.tzinfo is None:
            completed = completed.replace(tzinfo=timezone.utc)
        return (datetime.now(timezone.utc) - completed).days

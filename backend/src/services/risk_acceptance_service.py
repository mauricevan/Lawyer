"""Risk acceptance workflow validation (plan15 AB)."""
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from backend.src.utils.risk_acceptance_config import load_risk_acceptance_register, repo_root


class RiskAcceptanceService:
    """Validates risk decisions and 24h logging SLA."""

    def __init__(self, root: Path | None = None) -> None:
        self._root = root or repo_root()
        self._register = load_risk_acceptance_register()

    def build_summary(self) -> dict[str, Any]:
        rows = [self._row(entry) for entry in self._register.get("decisions", [])]
        logged = sum(1 for row in rows if row["logged_within_sla"])
        return {
            "decision_count": len(rows),
            "logged_within_sla": logged,
            "sla_compliance_ratio": round(logged / len(rows), 4) if rows else 1.0,
            "decisions": rows,
        }

    def audit(self) -> dict[str, Any]:
        summary = self.build_summary()
        issues = self._collect_issues(summary)
        gate = self._register.get("gate", {})
        max_hours = int(gate.get("max_decision_age_hours", 24))
        passed = summary["sla_compliance_ratio"] == 1.0 and not issues
        return {
            "suite": "risk_acceptance",
            "passed": passed,
            "summary": summary,
            "issues": issues,
            "gate": {"max_decision_age_hours": max_hours, "passed": passed},
        }

    def summarize_admin(self) -> dict[str, Any]:
        summary = self.build_summary()
        return {
            "decision_count": summary["decision_count"],
            "sla_compliance_ratio": summary["sla_compliance_ratio"],
            "open_deferred": [row["id"] for row in summary["decisions"] if row["decision"] == "defer"],
        }

    def _row(self, entry: dict[str, Any]) -> dict[str, Any]:
        decided = datetime.fromisoformat(str(entry["decided_at"]))
        if decided.tzinfo is None:
            decided = decided.replace(tzinfo=timezone.utc)
        age_hours = (datetime.now(timezone.utc) - decided).total_seconds() / 3600
        gate = self._register.get("gate", {})
        within_sla = age_hours <= int(gate.get("max_decision_age_hours", 24))
        owner_ok = bool(entry.get("owner")) if gate.get("require_owner", True) else True
        return {
            "id": entry.get("id"),
            "decision": entry.get("decision"),
            "owner": entry.get("owner"),
            "age_hours": round(age_hours, 2),
            "logged_within_sla": within_sla and owner_ok,
        }

    def _collect_issues(self, summary: dict[str, Any]) -> list[str]:
        issues: list[str] = []
        for row in summary["decisions"]:
            if not row["logged_within_sla"]:
                issues.append(f"{row['id']}: SLA or owner violation")
        return issues

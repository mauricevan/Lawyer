"""Tier-1 alert runbook coverage and playbook audit (plan14 AD)."""
from pathlib import Path
from typing import Any

import yaml

from backend.src.utils.alert_runbook_config import load_alert_runbook_policy, repo_root


class IncidentResponseService:
    """Audits alert-runbook links and exposes admin coverage metrics."""

    def __init__(self, root: Path | None = None) -> None:
        self._root = root or repo_root()
        self._policy = load_alert_runbook_policy()

    def build_coverage(self) -> dict[str, Any]:
        tier1 = self._policy.get("tier1_alerts", [])
        prometheus = self._load_prometheus_alerts()
        rows = [self._coverage_row(alert, prometheus) for alert in tier1]
        linked = sum(1 for row in rows if row["linked"])
        total = len(rows) or 1
        ratio = round(linked / total, 4)
        return {
            "tier1_alert_count": len(rows),
            "linked_count": linked,
            "coverage_ratio": ratio,
            "alerts": rows,
        }

    def audit(self) -> dict[str, Any]:
        coverage = self.build_coverage()
        issues = self._collect_issues(coverage)
        gate = self._policy.get("gate", {})
        min_ratio = float(gate.get("min_coverage_ratio", 1.0))
        passed = coverage["coverage_ratio"] >= min_ratio and not issues
        return {
            "suite": "incident_playbook_audit",
            "passed": passed,
            "coverage": coverage,
            "playbooks_ok": self._playbooks_ok(),
            "issues": issues,
            "gate": {"min_coverage_ratio": min_ratio, "passed": passed},
        }

    def summarize_admin(self, coverage: dict[str, Any] | None = None) -> dict[str, Any]:
        payload = coverage or self.build_coverage()
        unlinked = [row["id"] for row in payload["alerts"] if not row["linked"]]
        return {
            "coverage_ratio": payload["coverage_ratio"],
            "tier1_alert_count": payload["tier1_alert_count"],
            "linked_count": payload["linked_count"],
            "unlinked_alerts": unlinked,
            "alerts": payload["alerts"],
        }

    def _coverage_row(self, alert: dict[str, Any], prometheus: dict[str, Any]) -> dict[str, Any]:
        alert_id = str(alert["id"])
        runbook = str(alert.get("runbook", ""))
        playbook = str(alert.get("playbook", ""))
        prom = prometheus.get(alert_id, {})
        runbook_exists = (self._root / runbook).is_file()
        playbook_exists = (self._root / playbook).is_file()
        has_url = bool(prom.get("runbook_url"))
        linked = runbook_exists and playbook_exists and has_url
        return {
            "id": alert_id,
            "severity": alert.get("severity"),
            "runbook": runbook,
            "playbook": playbook,
            "runbook_exists": runbook_exists,
            "playbook_exists": playbook_exists,
            "prometheus_runbook_url": prom.get("runbook_url"),
            "linked": linked,
        }

    def _collect_issues(self, coverage: dict[str, Any]) -> list[str]:
        issues: list[str] = []
        for row in coverage["alerts"]:
            if row["linked"]:
                continue
            issues.append(f"{row['id']}: missing runbook link or file")
        for playbook in self._policy.get("required_playbooks", []):
            if not (self._root / str(playbook)).is_file():
                issues.append(f"missing required playbook: {playbook}")
        return issues

    def _playbooks_ok(self) -> bool:
        return all((self._root / str(path)).is_file() for path in self._policy.get("required_playbooks", []))

    def _load_prometheus_alerts(self) -> dict[str, dict[str, str]]:
        rel = str(self._policy.get("prometheus_alerts_path", "observability/prometheus/alerts.yml"))
        path = self._root / rel
        if not path.is_file():
            return {}
        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        indexed: dict[str, dict[str, str]] = {}
        for group in data.get("groups", []):
            for rule in group.get("rules", []):
                if "alert" not in rule:
                    continue
                annotations = rule.get("annotations", {}) or {}
                indexed[str(rule["alert"])] = {
                    "runbook_url": str(annotations.get("runbook_url", "")),
                }
        return indexed

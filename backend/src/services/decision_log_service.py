"""Unified decision log audit (plan15 AC)."""
from pathlib import Path
from typing import Any

from backend.src.utils.decision_log_config import load_decision_log_index, repo_root


class DecisionLogService:
    """Audits linked ADR, policy, and cycle decisions."""

    def __init__(self, root: Path | None = None) -> None:
        self._root = root or repo_root()
        self._index = load_decision_log_index()

    def build_coverage(self) -> dict[str, Any]:
        rows = [self._row(entry) for entry in self._index.get("entries", [])]
        linked = sum(1 for row in rows if row["linked"])
        total = len(rows) or 1
        return {
            "entry_count": len(rows),
            "linked_count": linked,
            "coverage_ratio": round(linked / total, 4),
            "entries": rows,
        }

    def audit(self) -> dict[str, Any]:
        coverage = self.build_coverage()
        gate = self._index.get("gate", {})
        min_entries = int(gate.get("min_linked_entries", 3))
        issues = [f"missing: {row['id']}" for row in coverage["entries"] if not row["linked"]]
        passed = coverage["linked_count"] >= min_entries and not issues
        return {
            "suite": "decision_log_audit",
            "passed": passed,
            "coverage": coverage,
            "issues": issues,
            "gate": {"min_linked_entries": min_entries, "passed": passed},
        }

    def summarize_admin(self) -> dict[str, Any]:
        coverage = self.build_coverage()
        return {
            "entry_count": coverage["entry_count"],
            "linked_count": coverage["linked_count"],
            "coverage_ratio": coverage["coverage_ratio"],
        }

    def _row(self, entry: dict[str, Any]) -> dict[str, Any]:
        rel = str(entry.get("path", ""))
        exists = (self._root / rel).is_file()
        return {
            "id": entry.get("id"),
            "type": entry.get("type"),
            "plan": entry.get("plan"),
            "path": rel,
            "linked": exists,
        }

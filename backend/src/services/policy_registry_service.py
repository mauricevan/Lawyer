"""Policy-as-code registry validation and coverage (plan15 AA)."""
from pathlib import Path
from typing import Any

import yaml

from backend.src.utils.policy_registry_config import load_policy_registry, repo_root


class PolicyRegistryService:
    """Validates registered policy files and reports governance coverage."""

    def __init__(self, root: Path | None = None) -> None:
        self._root = root or repo_root()
        self._registry = load_policy_registry()

    def build_coverage(self) -> dict[str, Any]:
        rows = [self._validate_entry(entry) for entry in self._registry.get("policies", [])]
        valid = sum(1 for row in rows if row["valid"])
        total = len(rows) or 1
        return {
            "registered_count": len(rows),
            "valid_count": valid,
            "coverage_ratio": round(valid / total, 4),
            "policies": rows,
        }

    def audit(self) -> dict[str, Any]:
        coverage = self.build_coverage()
        gate = self._registry.get("gate", {})
        min_ratio = float(gate.get("min_coverage_ratio", 0.95))
        issues = [row["issues"] for row in coverage["policies"] if not row["valid"]]
        flat_issues = [item for group in issues for item in group]
        passed = coverage["coverage_ratio"] >= min_ratio and not flat_issues
        return {
            "suite": "policy_registry",
            "passed": passed,
            "coverage": coverage,
            "issues": flat_issues,
            "gate": {"min_coverage_ratio": min_ratio, "passed": passed},
        }

    def summarize_admin(self, coverage: dict[str, Any] | None = None) -> dict[str, Any]:
        payload = coverage or self.build_coverage()
        invalid = [row["id"] for row in payload["policies"] if not row["valid"]]
        return {
            "coverage_ratio": payload["coverage_ratio"],
            "registered_count": payload["registered_count"],
            "valid_count": payload["valid_count"],
            "invalid_policies": invalid,
            "policies": [
                {
                    "id": row["id"],
                    "domain": row["domain"],
                    "plan": row["plan"],
                    "status": "valid" if row["valid"] else "invalid",
                }
                for row in payload["policies"]
            ],
        }

    def _validate_entry(self, entry: dict[str, Any]) -> dict[str, Any]:
        rel_path = str(entry.get("path", ""))
        path = self._root / rel_path
        issues: list[str] = []
        payload: dict[str, Any] = {}
        if not path.is_file():
            issues.append(f"missing file: {rel_path}")
        else:
            payload = self._load_policy(path, issues)
            self._check_version(payload, issues)
            self._check_required_keys(payload, entry.get("required_keys", []), issues)
        return {
            "id": entry.get("id"),
            "path": rel_path,
            "domain": entry.get("domain"),
            "plan": entry.get("plan"),
            "valid": not issues,
            "issues": issues,
        }

    def _load_policy(self, path: Path, issues: list[str]) -> dict[str, Any]:
        try:
            return yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        except yaml.YAMLError as exc:
            issues.append(f"invalid yaml: {exc.__class__.__name__}")
            return {}

    def _check_version(self, payload: dict[str, Any], issues: list[str]) -> None:
        gate = self._registry.get("gate", {})
        if not gate.get("require_version_field", True):
            return
        version = payload.get("version")
        if not version:
            issues.append("missing version field")

    def _check_required_keys(self, payload: dict[str, Any], keys: list[str], issues: list[str]) -> None:
        for key in keys:
            if key not in payload:
                issues.append(f"missing required key: {key}")

"""Generic cycle plan gate validation (plan16–plan30)."""
from pathlib import Path
from typing import Any

import yaml

_REPO = Path(__file__).resolve().parents[3]
_PLANS_DIR = _REPO / "shared/config/cycle_plans"


class CyclePlanGateService:
    """Audits per-plan cycle deliverables defined in YAML manifests."""

    def __init__(self, root: Path | None = None) -> None:
        self._root = root or _REPO

    def audit_plan(self, plan_id: str) -> dict[str, Any]:
        manifest = self._load_manifest(plan_id)
        artifacts = [self._check_artifact(item) for item in manifest.get("artifacts", [])]
        valid = sum(1 for row in artifacts if row["valid"])
        total = len(artifacts) or 1
        ratio = round(valid / total, 4)
        gate = manifest.get("gate", {})
        min_ratio = float(gate.get("min_artifact_ratio", 1.0))
        issues = [f"{row['id']}: invalid" for row in artifacts if not row["valid"]]
        passed = ratio >= min_ratio and not issues
        return {
            "suite": f"cycle_plan_{plan_id}",
            "plan_id": plan_id,
            "title": manifest.get("title"),
            "passed": passed,
            "artifact_ratio": ratio,
            "artifacts": artifacts,
            "issues": issues,
        }

    def audit_all(self) -> dict[str, Any]:
        registry = yaml.safe_load((_PLANS_DIR / "registry.yaml").read_text(encoding="utf-8"))
        results = [self.audit_plan(plan_id) for plan_id in registry.get("plans", [])]
        passed_count = sum(1 for row in results if row["passed"])
        gate = registry.get("gate", {})
        min_plans = int(gate.get("min_plans_passed", len(results)))
        passed = passed_count >= min_plans
        return {
            "suite": "cycle_plans",
            "passed": passed,
            "plan_count": len(results),
            "passed_count": passed_count,
            "results": results,
            "gate": {"min_plans_passed": min_plans, "passed": passed},
        }

    def _load_manifest(self, plan_id: str) -> dict[str, Any]:
        path = _PLANS_DIR / f"{plan_id}.yaml"
        if not path.is_file():
            return {"artifacts": [], "gate": {}}
        return yaml.safe_load(path.read_text(encoding="utf-8")) or {}

    def _check_artifact(self, item: dict[str, Any]) -> dict[str, Any]:
        rel = str(item.get("path", ""))
        path = self._root / rel
        issues: list[str] = []
        if not path.is_file():
            issues.append("missing file")
        elif item.get("type", "yaml") == "yaml":
            payload = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
            if not payload.get("version"):
                issues.append("missing version")
            for key in item.get("required_keys", []):
                if key not in payload:
                    issues.append(f"missing key {key}")
        return {
            "id": item.get("id"),
            "path": rel,
            "valid": not issues,
            "issues": issues,
        }

"""Strategic risk register helpers (plan9 V)."""
from pathlib import Path
from typing import Any

import yaml


class StrategicRiskService:
    """Evaluates strategic risks and escalation thresholds."""

    def __init__(self, register_path: Path | None = None) -> None:
        root = Path(__file__).resolve().parents[3]
        self._register_path = register_path or root / "docs/risk/strategic-risk-register.yaml"

    def load_register(self) -> dict[str, Any]:
        with open(self._register_path, encoding="utf-8") as handle:
            return yaml.safe_load(handle)

    def exposure(self, likelihood: int, impact: int) -> int:
        return int(likelihood) * int(impact)

    def high_risks(self, threshold: int | None = None) -> list[dict[str, Any]]:
        data = self.load_register()
        limit = threshold or int(data.get("scoring", {}).get("escalate_if", 12))
        output: list[dict[str, Any]] = []
        for risk in data.get("risks", []):
            score = self.exposure(risk["likelihood"], risk["impact"])
            if score >= limit:
                output.append({**risk, "exposure": score})
        return sorted(output, key=lambda row: -row["exposure"])

    def validate_register(self) -> list[str]:
        errors: list[str] = []
        data = self.load_register()
        ids: set[str] = set()
        for risk in data.get("risks", []):
            risk_id = risk.get("id", "")
            if risk_id in ids:
                errors.append(f"duplicate risk id: {risk_id}")
            ids.add(risk_id)
            if not risk.get("mitigation"):
                errors.append(f"{risk_id}: missing mitigation")
        return errors

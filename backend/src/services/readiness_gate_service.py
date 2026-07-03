"""Readiness pass-rate gate evaluation (plan14 KPI close)."""
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import httpx

from backend.src.utils.readiness_config import load_readiness_policy


class ReadinessGateService:
    """Evaluates readiness probe pass rate against SLO."""

    def __init__(self) -> None:
        self._policy = load_readiness_policy()

    def evaluate_samples(self, samples: list[bool], mode: str) -> dict[str, Any]:
        gate = self._policy.get("gate", {})
        min_rate = float(gate.get("min_pass_rate", 0.99))
        min_samples = int(gate.get("min_samples", 3))
        passed_count = sum(1 for sample in samples if sample)
        total = len(samples)
        rate = round(passed_count / total, 4) if total else 0.0
        violations: list[str] = []
        if total < min_samples:
            violations.append(f"samples {total} < min_samples {min_samples}")
        if rate < min_rate:
            violations.append(f"pass_rate {rate} < min_pass_rate {min_rate}")
        return {
            "suite": "readiness_pass_rate",
            "mode": mode,
            "passed": not violations,
            "samples_total": total,
            "samples_passed": passed_count,
            "pass_rate": rate,
            "min_pass_rate": min_rate,
            "violations": violations,
            "completed_at": datetime.now(timezone.utc).isoformat(),
        }

    def simulate_report(self) -> dict[str, Any]:
        min_samples = int(self._policy.get("gate", {}).get("min_samples", 3))
        return self.evaluate_samples([True] * min_samples, "simulate")

    async def probe_live(self, backend_url: str, sample_count: int) -> list[bool]:
        samples: list[bool] = []
        async with httpx.AsyncClient(base_url=backend_url, timeout=10.0) as client:
            for _ in range(sample_count):
                try:
                    response = await client.get("/ready")
                    samples.append(response.status_code == 200)
                except httpx.HTTPError:
                    samples.append(False)
        return samples

    def write_report(self, payload: dict[str, Any], report_path: Path) -> None:
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    def report_path(self) -> Path:
        gate = self._policy.get("gate", {})
        rel = str(gate.get("report_path", "docs/data/reliability-reports/readiness-pass-rate-latest.json"))
        root = Path(__file__).resolve().parents[3]
        return root / rel

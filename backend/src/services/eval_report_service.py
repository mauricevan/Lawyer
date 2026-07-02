"""Eval report generation and baseline comparison (plan7 O)."""
from pathlib import Path
from typing import Any

import yaml


class EvalReportService:
    """Compares eval suites against baseline and thresholds."""

    def __init__(
        self,
        thresholds_path: Path | None = None,
        baseline_path: Path | None = None,
    ) -> None:
        root = Path(__file__).resolve().parents[3]
        self._thresholds_path = thresholds_path or root / "docs/data/eval-thresholds.yaml"
        self._baseline_path = baseline_path or root / "backend/tests/fixtures/eval_baseline.json"

    def load_thresholds(self) -> dict[str, Any]:
        with open(self._thresholds_path, encoding="utf-8") as handle:
            return yaml.safe_load(handle)

    def load_baseline(self) -> dict[str, Any]:
        import json

        return json.loads(self._baseline_path.read_text(encoding="utf-8"))

    def compare_suite(
        self,
        suite_name: str,
        current: dict[str, float],
        baseline: dict[str, Any],
        thresholds: dict[str, Any],
    ) -> dict[str, Any]:
        suite_threshold = thresholds["suites"].get(suite_name, {})
        base = baseline.get("suites", {}).get(suite_name, {})
        max_regression = float(suite_threshold.get("max_regression", 0.05))
        regressions: list[str] = []
        for metric in ("recall_at_5", "mrr"):
            if metric not in current:
                continue
            floor_key = "recall_at_5_min" if metric == "recall_at_5" else "mrr_min"
            if floor_key in suite_threshold:
                min_val = float(suite_threshold[floor_key])
                if current[metric] < min_val:
                    regressions.append(f"{metric} {current[metric]:.3f} below min {min_val}")
            base_val = float(base.get(metric, current[metric]))
            if current[metric] < base_val - max_regression:
                regressions.append(
                    f"{metric} regressed {base_val:.3f} → {current[metric]:.3f}"
                )
        return {
            "suite": suite_name,
            "current": current,
            "baseline": base,
            "passed": len(regressions) == 0,
            "regressions": regressions,
        }

    def build_report(self, suite_results: dict[str, dict[str, float]]) -> dict[str, Any]:
        thresholds = self.load_thresholds()
        baseline = self.load_baseline()
        comparisons = [
            self.compare_suite(name, metrics, baseline, thresholds)
            for name, metrics in suite_results.items()
        ]
        return {
            "version": baseline.get("version", "unknown"),
            "passed": all(row["passed"] for row in comparisons),
            "suites": comparisons,
        }

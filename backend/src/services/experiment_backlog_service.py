"""Experiment backlog management (plan9 U)."""
from pathlib import Path
from typing import Any

import yaml


class ExperimentBacklogService:
    """Loads and validates innovation experiments."""

    def __init__(self, backlog_path: Path | None = None, budget_path: Path | None = None) -> None:
        root = Path(__file__).resolve().parents[3]
        self._backlog_path = backlog_path or root / "docs/product/experiment-backlog.yaml"
        self._budget_path = budget_path or root / "docs/product/innovation-budget.yaml"

    def load_backlog(self) -> dict[str, Any]:
        with open(self._backlog_path, encoding="utf-8") as handle:
            return yaml.safe_load(handle)

    def load_budget(self) -> dict[str, Any]:
        with open(self._budget_path, encoding="utf-8") as handle:
            return yaml.safe_load(handle)

    def active_experiments(self) -> list[dict[str, Any]]:
        data = self.load_backlog()
        return [exp for exp in data.get("experiments", []) if exp.get("status") == "active"]

    def can_start_experiment(self) -> tuple[bool, str]:
        budget = self.load_budget()
        max_active = int(budget["allocation"]["max_active_experiments"])
        active = len(self.active_experiments())
        if active >= max_active:
            return False, f"active experiments {active} >= max {max_active}"
        return True, "ok"

    def validate_experiment(self, experiment: dict[str, Any]) -> list[str]:
        errors: list[str] = []
        for field in ("id", "title", "hypothesis", "success_metric", "stop_go"):
            if not experiment.get(field):
                errors.append(f"missing field: {field}")
        weeks = int(experiment.get("max_weeks", 0))
        budget = self.load_budget()
        max_weeks = int(budget["allocation"]["max_weeks_per_experiment"])
        if weeks > max_weeks:
            errors.append(f"max_weeks {weeks} exceeds budget {max_weeks}")
        return errors

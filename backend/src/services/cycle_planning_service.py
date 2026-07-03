"""Cycle planning and plan transition helpers (plan10 W)."""
from datetime import date, datetime
from pathlib import Path
from typing import Any

import yaml


class CyclePlanningService:
    """Validates plan transitions and relevance reviews."""

    def __init__(self, cycle_root: Path | None = None) -> None:
        root = Path(__file__).resolve().parents[3]
        self._cycle_root = cycle_root or root / "docs/cycle"
        self._repo_root = root

    def load_relevance_review(self) -> dict[str, Any]:
        path = self._cycle_root / "plan-relevance-review.yaml"
        with open(path, encoding="utf-8") as handle:
            return yaml.safe_load(handle)

    def load_legacy_register(self) -> dict[str, Any]:
        path = self._cycle_root / "legacy-cleanup-register.yaml"
        with open(path, encoding="utf-8") as handle:
            return yaml.safe_load(handle)

    def validate_plan_transition(self, completed_plan: str) -> list[str]:
        errors: list[str] = []
        plan_path = self._repo_root / f"{completed_plan}.md"
        if not plan_path.is_file():
            errors.append(f"missing plan file: {completed_plan}.md")
        themes_path = self._cycle_root / "next-cycle-themes.yaml"
        if not themes_path.is_file():
            errors.append("missing next-cycle-themes.yaml")
            return errors
        with open(themes_path, encoding="utf-8") as handle:
            themes = yaml.safe_load(handle)
        previous = themes.get("previous_plan", "")
        expected = f"{completed_plan}.md"
        if previous and previous != expected:
            errors.append(f"next-cycle-themes previous_plan={previous} != {expected}")
        start = themes.get("formal_start", {})
        for key in ("kickoff_doc", "exit_review_doc"):
            rel = start.get(key)
            if rel and not (self._repo_root / rel).is_file():
                errors.append(f"missing {key}: {rel}")
        return errors

    def stale_reviews(self, today: date | None = None) -> list[str]:
        data = self.load_relevance_review()
        threshold = int(data.get("stale_threshold_days", 120))
        current = today or date.today()
        stale: list[str] = []
        for row in data.get("reviews", []):
            reviewed = datetime.strptime(row["last_reviewed"], "%Y-%m-%d").date()
            if (current - reviewed).days > threshold:
                stale.append(row["plan_file"])
        return stale

    def open_legacy_count(self) -> int:
        data = self.load_legacy_register()
        return sum(1 for item in data.get("items", []) if item.get("status") == "open")

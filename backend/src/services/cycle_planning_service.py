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
        plan_path = Path(__file__).resolve().parents[3] / f"{completed_plan}.md"
        if not plan_path.is_file():
            errors.append(f"missing plan file: {completed_plan}.md")
        kickoff = self._cycle_root / "plan11-kickoff.md"
        if completed_plan == "plan9" and not kickoff.is_file():
            errors.append("plan9→plan10: plan11-kickoff not required yet")
        themes = self._cycle_root / "next-cycle-themes.yaml"
        if not themes.is_file():
            errors.append("missing next-cycle-themes.yaml")
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

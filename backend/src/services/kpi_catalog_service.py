"""KPI catalog — leading and lagging indicators (plan10 X)."""
from pathlib import Path
from typing import Any

import yaml


class KpiCatalogService:
    """Loads KPI catalog and classifies indicator types."""

    def __init__(self, catalog_path: Path | None = None) -> None:
        root = Path(__file__).resolve().parents[3]
        self._catalog_path = catalog_path or root / "docs/cycle/kpi-catalog.yaml"

    def load_catalog(self) -> dict[str, Any]:
        with open(self._catalog_path, encoding="utf-8") as handle:
            return yaml.safe_load(handle)

    def leading_indicators(self) -> list[dict[str, Any]]:
        return self._by_type("leading")

    def lagging_indicators(self) -> list[dict[str, Any]]:
        return self._by_type("lagging")

    def _by_type(self, indicator_type: str) -> list[dict[str, Any]]:
        data = self.load_catalog()
        return [
            row for row in data.get("indicators", [])
            if row.get("type") == indicator_type
        ]

    def validate_catalog(self) -> list[str]:
        errors: list[str] = []
        data = self.load_catalog()
        ids: set[str] = set()
        for row in data.get("indicators", []):
            row_id = row.get("id", "")
            if row_id in ids:
                errors.append(f"duplicate indicator id: {row_id}")
            ids.add(row_id)
            if row.get("type") not in {"leading", "lagging"}:
                errors.append(f"{row_id}: invalid type")
            if not row.get("corrective_playbook"):
                errors.append(f"{row_id}: missing corrective_playbook")
        leading = len(self.leading_indicators())
        lagging = len(self.lagging_indicators())
        if leading < 2 or lagging < 2:
            errors.append("catalog needs at least 2 leading and 2 lagging indicators")
        return errors

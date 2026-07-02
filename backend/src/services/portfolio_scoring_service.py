"""Portfolio initiative scoring (plan9 T)."""
from pathlib import Path
from typing import Any

import yaml


class PortfolioScoringService:
    """Scores initiatives using impact, risk reduction, and effort."""

    def __init__(self, model_path: Path | None = None) -> None:
        root = Path(__file__).resolve().parents[3]
        self._model_path = model_path or root / "docs/product/prioritization-model.yaml"

    def load_model(self) -> dict[str, Any]:
        with open(self._model_path, encoding="utf-8") as handle:
            return yaml.safe_load(handle)

    def score_initiative(
        self,
        impact: int,
        risk_reduction: int,
        effort: int,
    ) -> float:
        model = self.load_model()
        weights = model["weights"]
        effort_inverse = max(1, min(5, 6 - effort))
        return round(
            impact * weights["impact"]
            + risk_reduction * weights["risk_reduction"]
            + effort_inverse * weights["effort_inverse"],
            3,
        )

    def should_schedule(self, score: float) -> bool:
        model = self.load_model()
        return score >= float(model.get("minimum_score_to_schedule", 2.5))

    def rank_initiatives(self, items: list[dict[str, int]]) -> list[dict[str, Any]]:
        ranked = []
        for item in items:
            score = self.score_initiative(
                int(item["impact"]),
                int(item["risk_reduction"]),
                int(item["effort"]),
            )
            ranked.append({**item, "score": score, "schedule": self.should_schedule(score)})
        return sorted(ranked, key=lambda row: (-row["score"], row["effort"]))

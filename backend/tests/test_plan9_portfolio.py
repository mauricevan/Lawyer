"""Tests for plan9 portfolio, innovation, and risk artifacts."""
from pathlib import Path

import yaml

from backend.src.services.experiment_backlog_service import ExperimentBacklogService
from backend.src.services.portfolio_scoring_service import PortfolioScoringService
from backend.src.services.strategic_risk_service import StrategicRiskService

_REPO = Path(__file__).resolve().parents[2]


def test_prioritization_model_loads() -> None:
    data = yaml.safe_load((_REPO / "docs/product/prioritization-model.yaml").read_text(encoding="utf-8"))
    assert "weights" in data


def test_portfolio_scoring_ranks_higher_impact_first() -> None:
    service = PortfolioScoringService()
    ranked = service.rank_initiatives([
        {"id": "a", "impact": 5, "risk_reduction": 4, "effort": 2},
        {"id": "b", "impact": 2, "risk_reduction": 2, "effort": 5},
    ])
    assert ranked[0]["id"] == "a"
    assert ranked[0]["score"] > ranked[1]["score"]


def test_experiment_backlog_validates_entries() -> None:
    service = ExperimentBacklogService()
    data = service.load_backlog()
    assert len(data["experiments"]) >= 2
    assert not service.validate_experiment(data["experiments"][0])


def test_strategic_risk_register_loads() -> None:
    service = StrategicRiskService()
    assert not service.validate_register()
    assert len(service.load_register()["risks"]) >= 4


def test_plan9_scripts_exist() -> None:
    scripts = [
        "scripts/ops/run-portfolio-board-review.sh",
        "scripts/ops/run-innovation-pipeline-check.sh",
        "scripts/ops/run-strategic-risk-review.sh",
    ]
    for script in scripts:
        assert (_REPO / script).is_file()

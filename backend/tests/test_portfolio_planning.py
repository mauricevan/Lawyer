"""Tests for portfolio planning artifacts (plan5 J1)."""
from pathlib import Path

import yaml

_REPO_ROOT = Path(__file__).resolve().parents[2]
_METRICS_PATH = _REPO_ROOT / "docs/product/portfolio-metrics.yaml"


def test_portfolio_metrics_loads_objectives() -> None:
    data = yaml.safe_load(_METRICS_PATH.read_text(encoding="utf-8"))
    ids = {item["id"] for item in data["objectives"]}
    assert "retrieval_quality" in ids
    assert "negative_feedback_ratio" in ids


def test_portfolio_metrics_includes_feedback_and_regression() -> None:
    data = yaml.safe_load(_METRICS_PATH.read_text(encoding="utf-8"))
    ids = {item["id"] for item in data["objectives"]}
    assert "positive_feedback_score" in ids
    assert "regression_rate" in ids


def test_capacity_allocation_sums_to_one() -> None:
    data = yaml.safe_load(_METRICS_PATH.read_text(encoding="utf-8"))
    for mode, buckets in data["capacity_allocation"].items():
        total = sum(buckets.values())
        assert abs(total - 1.0) < 0.01, f"{mode} allocation invalid"

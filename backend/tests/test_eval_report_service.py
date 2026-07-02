"""Tests for eval report service (plan7 O)."""
from pathlib import Path

from backend.src.services.eval_report_service import EvalReportService

_REPO = Path(__file__).resolve().parents[2]


def test_compare_suite_passes_at_baseline() -> None:
    service = EvalReportService()
    thresholds = service.load_thresholds()
    baseline = service.load_baseline()
    result = service.compare_suite(
        "retrieval",
        {"recall_at_5": 0.82, "mrr": 0.72},
        baseline,
        thresholds,
    )
    assert result["passed"] is True


def test_compare_suite_flags_regression() -> None:
    service = EvalReportService()
    thresholds = service.load_thresholds()
    baseline = service.load_baseline()
    result = service.compare_suite(
        "retrieval",
        {"recall_at_5": 0.50, "mrr": 0.40},
        baseline,
        thresholds,
    )
    assert result["passed"] is False
    assert result["regressions"]


def test_build_report_aggregates_suites() -> None:
    service = EvalReportService()
    report = service.build_report({
        "retrieval": {"recall_at_5": 0.82, "mrr": 0.72},
        "multilingual": {"recall_at_5": 0.75, "mrr": 0.68},
    })
    assert report["passed"] is True
    assert len(report["suites"]) == 2


def test_plan7_governance_docs_exist() -> None:
    paths = [
        _REPO / "docs/data/dataset-changelog.md",
        _REPO / "docs/data/data-lineage.md",
        _REPO / "docs/data/domain-data-owners.yaml",
        _REPO / "shared/config/prompts.yaml",
        _REPO / "scripts/qa/rollback-prompt-config.sh",
    ]
    for path in paths:
        assert path.is_file(), f"missing {path}"

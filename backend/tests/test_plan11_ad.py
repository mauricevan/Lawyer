"""Tests for plan11 AD CI integration eval and stack-aware release."""
from pathlib import Path

import yaml

_REPO = Path(__file__).resolve().parents[2]


def test_integration_eval_scripts_exist() -> None:
    scripts = (
        "scripts/qa/run-integration-eval-gate.sh",
        "scripts/qa/run-stack-aware-eval.sh",
        "scripts/qa/check-eval-stack.sh",
    )
    for script in scripts:
        assert (_REPO / script).is_file()


def test_ci_workflow_includes_integration_eval() -> None:
    workflow = (_REPO / ".github/workflows/ci.yml").read_text(encoding="utf-8")
    assert "integration-eval:" in workflow
    assert "run-integration-eval-gate.sh" in workflow


def test_ci_subset_fixture_and_thresholds() -> None:
    fixture = _REPO / "backend/tests/fixtures/rag_eval_ci_subset.json"
    assert fixture.is_file()
    thresholds = yaml.safe_load(
        (_REPO / "docs/data/eval-thresholds.yaml").read_text(encoding="utf-8")
    )
    assert "ci_integration" in thresholds["suites"]


def test_seed_ci_script_exists() -> None:
    assert (_REPO / "ingestion/scripts/seed_ci_eval_corpus.py").is_file()

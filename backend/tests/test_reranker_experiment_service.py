"""Tests for EXP-002 reranker promotion gate."""
from backend.src.services.reranker_experiment_service import RerankerExperimentService


def _metrics(mrr: float, recall: float, p95_ms: float) -> dict:
    return {"mrr": mrr, "recall_at_5": recall, "p95_retrieval_ms": p95_ms}


def test_gate_passes_at_ceiling_without_regression() -> None:
    service = RerankerExperimentService()
    result = service.evaluate_promotion_gate(
        _metrics(1.0, 1.0, 500.0),
        _metrics(1.0, 1.0, 800.0),
    )
    assert result["passed"] is True


def test_gate_fails_when_mrr_regresses_at_ceiling() -> None:
    service = RerankerExperimentService()
    result = service.evaluate_promotion_gate(
        _metrics(1.0, 1.0, 500.0),
        _metrics(0.98, 1.0, 800.0),
    )
    assert result["passed"] is False


def test_gate_requires_mrr_lift_below_ceiling() -> None:
    service = RerankerExperimentService()
    result = service.evaluate_promotion_gate(
        _metrics(0.80, 0.85, 500.0),
        _metrics(0.82, 0.85, 800.0),
    )
    assert result["passed"] is False
    improved = service.evaluate_promotion_gate(
        _metrics(0.80, 0.85, 500.0),
        _metrics(0.86, 0.85, 800.0),
    )
    assert improved["passed"] is True


def test_gate_fails_on_latency_budget() -> None:
    service = RerankerExperimentService()
    result = service.evaluate_promotion_gate(
        _metrics(1.0, 1.0, 500.0),
        _metrics(1.0, 1.0, 12000.0),
    )
    assert result["passed"] is False

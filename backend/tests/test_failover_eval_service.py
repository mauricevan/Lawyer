"""Unit tests for failover scenario evaluation (plan14 AB)."""
from backend.src.services.failover_eval_service import FailoverEvalService


def test_failover_eval_suite_passes():
    report = FailoverEvalService().run()
    assert report["passed"], report["failures"]


def test_failover_eval_covers_qdrant_loss():
    report = FailoverEvalService().run()
    ids = {row["id"] for row in report["results"]}
    assert "SCN-QDRANT-EMPTY" in ids
    assert "SCN-QDRANT-ERROR" in ids

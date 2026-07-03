"""Tests for reranker service and variant config."""
from typing import Any

import pytest

from backend.src.services.reranker_service import RerankerService
from backend.src.utils.reranker_config import list_variants, resolve_model_id


class _FakeEncoder:
    def __init__(self, model_id: str) -> None:
        self.model_id = model_id

    def predict(self, pairs: list[tuple[str, str]]) -> list[float]:
        return [float(len(text)) for _, text in pairs]


def _sample_results() -> list[dict[str, Any]]:
    return [
        {"text": "short", "celex": "A"},
        {"text": "much longer chunk text", "celex": "B"},
    ]


def test_list_variants_includes_control_and_candidate() -> None:
    variants = list_variants()
    assert "control" in variants
    assert "candidate" in variants


def test_resolve_model_id_for_control() -> None:
    model_id = resolve_model_id("control")
    assert "MiniLM" in model_id


def test_reranker_orders_by_model_scores() -> None:
    service = RerankerService(variant="control", model=_FakeEncoder("test"))
    ranked = service.rerank("query", _sample_results(), top_k=2)
    assert ranked[0]["celex"] == "B"
    assert service.last_latency_ms >= 0.0


def test_reranker_unknown_variant_raises() -> None:
    with pytest.raises(ValueError, match="Unknown reranker variant"):
        RerankerService(variant="missing", model=_FakeEncoder("x"))


def test_reranker_fallback_on_predict_error() -> None:
    class _BrokenEncoder:
        def predict(self, pairs: list[tuple[str, str]]) -> list[float]:
            raise RuntimeError("model unavailable")

    service = RerankerService(variant="control", model=_BrokenEncoder())
    ranked = service.rerank("query", _sample_results(), top_k=1)
    assert ranked[0]["celex"] == "A"

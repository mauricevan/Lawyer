"""Run retrieval eval per reranker variant (EXP-002)."""
import json
import time
from pathlib import Path
from typing import Any

from backend.src.services.rag_service import RagService
from backend.src.services.reranker_service import RerankerService
from backend.src.utils.retrieval_metrics import mean_reciprocal_rank, recall_at_k, summarize_eval_results
from shared.schemas.query import QueryRequest

_REPO = Path(__file__).resolve().parents[3]
_DEFAULT_FIXTURE = _REPO / "backend/tests/fixtures/rag_eval_questions.json"


class RerankerEvalService:
    """Measures retrieval quality and latency for a reranker variant."""

    def __init__(self, fixture_path: Path | None = None) -> None:
        self._fixture_path = fixture_path or _DEFAULT_FIXTURE

    async def evaluate_variant(self, variant: str) -> dict[str, Any]:
        rag = RagService()
        rag._reranker = RerankerService(variant=variant)
        questions = json.loads(self._fixture_path.read_text(encoding="utf-8"))
        rows: list[dict[str, float]] = []
        latencies_ms: list[float] = []
        for item in questions:
            routed = rag._route_request(QueryRequest(question=item["question"]))
            started = time.perf_counter()
            results, _ = await rag._retrieve(routed)
            latencies_ms.append((time.perf_counter() - started) * 1000)
            retrieved = [r.get("celex", "") for r in results]
            expected = set(item["expected_celex"])
            rows.append({
                "recall_at_5": recall_at_k(expected, retrieved, k=5),
                "mrr": mean_reciprocal_rank(expected, retrieved),
            })
        summary = summarize_eval_results(rows)
        summary["variant"] = variant
        summary["model_id"] = rag._reranker.model_id
        summary["p95_retrieval_ms"] = self._percentile(latencies_ms, 95)
        summary["avg_retrieval_ms"] = sum(latencies_ms) / len(latencies_ms) if latencies_ms else 0.0
        return summary

    @staticmethod
    def _percentile(values: list[float], pct: int) -> float:
        if not values:
            return 0.0
        ordered = sorted(values)
        index = max(0, int(len(ordered) * pct / 100) - 1)
        return ordered[index]

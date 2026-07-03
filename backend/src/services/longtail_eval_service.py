"""Long-tail retrieval eval runner (plan12 AD)."""
import json
from pathlib import Path
from typing import Any

from backend.src.services.eval_report_service import EvalReportService
from backend.src.services.rag_service import RagService
from backend.src.utils.retrieval_metrics import mean_reciprocal_rank, recall_at_k, summarize_eval_results
from shared.schemas.query import QueryFilters, QueryRequest

_REPO = Path(__file__).resolve().parents[3]
_DEFAULT_FIXTURE = _REPO / "backend/tests/fixtures/rag_eval_longtail.json"


class LongtailEvalService:
    """Evaluates retrieval on edge-case questions with YAML thresholds."""

    def __init__(self, fixture_path: Path | None = None) -> None:
        self._fixture_path = fixture_path or _DEFAULT_FIXTURE
        self._thresholds = EvalReportService().load_thresholds()["suites"]["longtail"]

    async def run(self) -> dict[str, Any]:
        items = json.loads(self._fixture_path.read_text(encoding="utf-8"))
        rag = RagService()
        rows: list[dict[str, float]] = []
        misses: list[str] = []
        for item in items:
            lang = item.get("language", "nl")
            filters = None
            if item.get("time_context"):
                filters = QueryFilters(
                    language=lang,
                    time_context=item["time_context"],
                    in_force_only=item["time_context"] != "historical",
                )
            request = QueryRequest(question=item["question"], language=lang, filters=filters)
            routed = rag._route_request(request)
            results, _ = await rag._retrieve(routed)
            retrieved = [r.get("celex", "") for r in results]
            expected = set(item["expected_celex"])
            rows.append({
                "recall_at_5": recall_at_k(expected, retrieved, k=5),
                "mrr": mean_reciprocal_rank(expected, retrieved),
            })
            if not set(retrieved).intersection(expected):
                misses.append(f"[{item.get('category', '?')}] {item['question'][:70]}")
        summary = summarize_eval_results(rows)
        failures = self._threshold_failures(summary)
        return {
            "passed": not failures,
            "summary": summary,
            "thresholds": self._thresholds,
            "failures": failures,
            "misses": misses,
            "count": len(items),
        }

    def _threshold_failures(self, summary: dict[str, float]) -> list[str]:
        failures: list[str] = []
        recall_min = float(self._thresholds.get("recall_at_5_min", 0.75))
        if summary["recall_at_5"] < recall_min:
            failures.append(f"recall_at_5 {summary['recall_at_5']:.3f} below {recall_min}")
        mrr_min = self._thresholds.get("mrr_min")
        if mrr_min is not None and summary["mrr"] < float(mrr_min):
            failures.append(f"mrr {summary['mrr']:.3f} below {mrr_min}")
        return failures

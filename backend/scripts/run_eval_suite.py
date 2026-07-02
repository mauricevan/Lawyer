#!/usr/bin/env python3
"""Run release eval suite with baseline comparison (plan7 O)."""
import argparse
import asyncio
import json
import sys
from pathlib import Path

from backend.src.services.eval_report_service import EvalReportService
from backend.src.services.rag_service import RagService
from backend.src.utils.retrieval_metrics import mean_reciprocal_rank, recall_at_k, summarize_eval_results
from shared.schemas.query import QueryRequest

ROOT = Path(__file__).resolve().parents[2]
REPORT_DIR = ROOT / "docs/data/eval-reports"
BASELINE_PATH = ROOT / "backend/tests/fixtures/eval_baseline.json"


async def _run_fixture(path: Path, language: str = "nl") -> dict[str, float]:
    items = json.loads(path.read_text(encoding="utf-8"))
    rag = RagService()
    rows = []
    for item in items:
        lang = item.get("language", language)
        request = QueryRequest(question=item["question"], language=lang)
        routed = rag._route_request(request)
        results, _ = await rag._retrieve(routed)
        retrieved = [r.get("celex", "") for r in results]
        expected = set(item["expected_celex"])
        rows.append({
            "recall_at_5": recall_at_k(expected, retrieved, k=5),
            "mrr": mean_reciprocal_rank(expected, retrieved),
        })
    return summarize_eval_results(rows)


async def run_suite() -> dict[str, dict[str, float]]:
    return {
        "retrieval": await _run_fixture(ROOT / "backend/tests/fixtures/rag_eval_questions.json"),
        "multilingual": await _run_fixture(ROOT / "backend/tests/fixtures/rag_eval_multilingual.json", "fr"),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Run eval suite and compare baseline")
    parser.add_argument("--update-baseline", action="store_true")
    args = parser.parse_args()
    suite_results = asyncio.run(run_suite())
    if args.update_baseline:
        payload = {
            "version": "2026.07.02",
            "captured_at": __import__("datetime").date.today().isoformat(),
            "suites": suite_results,
        }
        BASELINE_PATH.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        print(f"Updated baseline: {BASELINE_PATH}")
        return
    service = EvalReportService()
    report = service.build_report(suite_results)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    latest = REPORT_DIR / "latest.json"
    latest.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))
    if not report["passed"]:
        sys.exit("Eval suite failed regression checks")


if __name__ == "__main__":
    main()

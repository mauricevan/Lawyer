#!/usr/bin/env bash
# Per-domain retrieval benchmark and go/no-go report.
set -euo pipefail

cd "$(dirname "$0")/../.."
export PYTHONPATH=.

python3 - <<'PY'
import asyncio
import json
from pathlib import Path

from backend.src.services.domain_benchmark_service import DomainBenchmarkService
from backend.src.services.rag_service import RagService
from backend.src.utils.retrieval_metrics import mean_reciprocal_rank, recall_at_k
from shared.schemas.query import QueryRequest

fixture = Path("backend/tests/fixtures/rag_eval_questions.json")
questions = json.loads(fixture.read_text(encoding="utf-8"))
benchmark = DomainBenchmarkService()

async def run() -> None:
    rag = RagService()
    grouped = benchmark.group_questions(questions)
    domain_results = []
    for domain_id, items in sorted(grouped.items()):
        rows = []
        for item in items:
            routed = rag._route_request(QueryRequest(question=item["question"]))
            results, _ = await rag._retrieve(routed)
            retrieved = [r.get("celex", "") for r in results]
            expected = set(item["expected_celex"])
            rows.append({
                "recall_at_5": recall_at_k(expected, retrieved, k=5),
                "mrr": mean_reciprocal_rank(expected, retrieved),
            })
        domain_results.append(benchmark.evaluate_domain(domain_id, rows))
    report = benchmark.build_go_no_go_report(domain_results)
    print(json.dumps(report, indent=2, ensure_ascii=False))
    failing = [d for d in domain_results if d["decision"] == "fail" and d["status"] == "go"]
    if failing:
        names = ", ".join(row["domain"] for row in failing)
        raise SystemExit(f"Go-domain benchmark failed: {names}")

asyncio.run(run())
PY

#!/usr/bin/env bash
# Run retrieval eval with threshold gate (requires Qdrant + seeded corpus).
set -euo pipefail

cd "$(dirname "$0")/../.."
export PYTHONPATH=.

python3 - <<'PY'
import asyncio
import json
from pathlib import Path

from backend.src.config import settings
from backend.src.services.rag_service import RagService
from backend.src.utils.retrieval_metrics import mean_reciprocal_rank, recall_at_k, summarize_eval_results
from shared.schemas.query import QueryRequest

fixture = Path("backend/tests/fixtures/rag_eval_questions.json")
questions = json.loads(fixture.read_text(encoding="utf-8"))

async def run() -> None:
    rag = RagService()
    rows = []
    for item in questions:
        routed = rag._route_request(QueryRequest(question=item["question"]))
        results, _ = await rag._retrieve(routed)
        retrieved = [r.get("celex", "") for r in results]
        expected = set(item["expected_celex"])
        rows.append({
            "recall_at_5": recall_at_k(expected, retrieved, k=5),
            "mrr": mean_reciprocal_rank(expected, retrieved),
        })
    summary = summarize_eval_results(rows)
    print(json.dumps(summary, indent=2))
    if summary["recall_at_5"] < settings.eval_recall_at_5_min:
        raise SystemExit(f"Recall@5 {summary['recall_at_5']:.3f} below {settings.eval_recall_at_5_min}")
    if summary["mrr"] < settings.eval_mrr_min:
        raise SystemExit(f"MRR {summary['mrr']:.3f} below {settings.eval_mrr_min}")

asyncio.run(run())
PY

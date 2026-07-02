#!/usr/bin/env bash
# Multilingual retrieval benchmark for FR/DE/ES (plan5 I2).
set -euo pipefail

cd "$(dirname "$0")/../.."
export PYTHONPATH=.

python3 backend/scripts/build_multilingual_eval_fixture.py

python3 - <<'PY'
import asyncio
import json
from pathlib import Path

from backend.src.services.rag_service import RagService
from backend.src.utils.retrieval_metrics import mean_reciprocal_rank, recall_at_k
from shared.schemas.query import QueryRequest

fixture = Path("backend/tests/fixtures/rag_eval_multilingual.json")
questions = json.loads(fixture.read_text(encoding="utf-8"))

async def run() -> None:
    rag = RagService()
    grouped: dict[str, list[dict]] = {}
    for item in questions:
        lang = item.get("language", "nl")
        grouped.setdefault(lang, []).append(item)
    report: dict[str, object] = {"languages": {}, "passed": True}
    for language, items in sorted(grouped.items()):
        rows = []
        for item in items:
            request = QueryRequest(question=item["question"], language=language)
            routed = rag._route_request(request)
            results, _ = await rag._retrieve(routed)
            retrieved = [r.get("celex", "") for r in results]
            expected = set(item["expected_celex"])
            rows.append({
                "recall_at_5": recall_at_k(expected, retrieved, k=5),
                "mrr": mean_reciprocal_rank(expected, retrieved),
            })
        recall = sum(row["recall_at_5"] for row in rows) / len(rows)
        mrr = sum(row["mrr"] for row in rows) / len(rows)
        passed = recall >= 0.70
        report["languages"][language] = {
            "count": len(rows),
            "recall_at_5": recall,
            "mrr": mrr,
            "passed": passed,
        }
        if not passed:
            report["passed"] = False
    print(json.dumps(report, indent=2, ensure_ascii=False))
    if not report["passed"]:
        raise SystemExit("Multilingual benchmark below threshold for one or more languages")

asyncio.run(run())
PY

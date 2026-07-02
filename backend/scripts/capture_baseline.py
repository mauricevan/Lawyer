#!/usr/bin/env python3
"""Capture baseline latency and retrieval metrics for plan Fase 0."""
import asyncio
import json
import time
from pathlib import Path

from httpx import ASGITransport, AsyncClient

from backend.src.main import app
from backend.src.routes import query as query_route
from backend.src.services.rag_service import RagService
from backend.src.utils.retrieval_metrics import mean_reciprocal_rank, recall_at_k, summarize_eval_results
from shared.schemas.query import QueryRequest

FIXTURE = Path(__file__).resolve().parents[2] / "tests" / "fixtures" / "rag_eval_questions.json"
OUTPUT = Path(__file__).resolve().parents[2] / "tests" / "fixtures" / "baseline_metrics.json"


async def measure_api_latency() -> dict[str, float]:
    async def fake_query(body, history, session=None):
        from shared.schemas.query import AnswerResponse
        return AnswerResponse(answer="ok", conversation_id="x", citations=[]), [], []

    query_route.rag.query = fake_query
    transport = ASGITransport(app=app)
    timings: list[float] = []
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        for _ in range(5):
            started = time.perf_counter()
            await client.get("/health")
            timings.append((time.perf_counter() - started) * 1000)
    timings.sort()
    return {
        "health_p50_ms": timings[len(timings) // 2],
        "health_p95_ms": timings[max(0, int(len(timings) * 0.95) - 1)],
    }


async def measure_retrieval_sample() -> dict[str, float]:
    questions = json.loads(FIXTURE.read_text(encoding="utf-8"))[:20]
    rag = RagService()
    rows = []
    for item in questions:
        results, _route = await rag._retrieve(QueryRequest(question=item["question"]))
        retrieved = [r.get("celex", "") for r in results]
        expected = set(item["expected_celex"])
        rows.append({
            "recall_at_5": recall_at_k(expected, retrieved, k=5),
            "mrr": mean_reciprocal_rank(expected, retrieved),
        })
    return summarize_eval_results(rows)


async def main() -> None:
    baseline = {
        "api": await measure_api_latency(),
        "retrieval_sample_20": await measure_retrieval_sample(),
    }
    OUTPUT.write_text(json.dumps(baseline, indent=2), encoding="utf-8")
    print(json.dumps(baseline, indent=2))


if __name__ == "__main__":
    asyncio.run(main())

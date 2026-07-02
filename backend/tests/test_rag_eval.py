"""Retrieval evaluation against curated corpus expectations."""
import json
from pathlib import Path

import pytest

from backend.src.services.rag_service import RagService
from backend.src.utils.retrieval_metrics import mean_reciprocal_rank, recall_at_k, summarize_eval_results
from shared.schemas.query import QueryRequest

FIXTURE_PATH = Path(__file__).parent / "fixtures" / "rag_eval_questions.json"


@pytest.fixture
def eval_questions() -> list[dict]:
    return json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))


@pytest.mark.integration
@pytest.mark.asyncio
async def test_rag_retrieval_hits_expected_celex(eval_questions: list[dict]):
    """Each eval question should retrieve at least one chunk from expected CELEX."""
    rag = RagService()
    failures: list[str] = []
    metric_rows: list[dict] = []
    for item in eval_questions:
        request = rag._route_request(QueryRequest(question=item["question"], audience="professional"))
        results, _route = await rag._retrieve(request)
        retrieved_celex = [r.get("celex", "") for r in results]
        expected = set(item["expected_celex"])
        metric_rows.append({
            "recall_at_5": recall_at_k(expected, retrieved_celex, k=5),
            "mrr": mean_reciprocal_rank(expected, retrieved_celex),
        })
        if not set(retrieved_celex).intersection(expected):
            failures.append(f"{item['question'][:50]}... -> got {sorted(set(retrieved_celex))[:5]}")
    summary = summarize_eval_results(metric_rows)
    assert summary["count"] == float(len(eval_questions))
    assert not failures, "Retrieval misses:\n" + "\n".join(failures[:20])

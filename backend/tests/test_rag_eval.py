"""Retrieval evaluation against curated corpus expectations."""
import json
from pathlib import Path

import pytest

from backend.src.services.rag_service import RagService
from shared.schemas.query import QueryRequest

FIXTURE_PATH = Path(__file__).parent / "fixtures" / "rag_eval_questions.json"


@pytest.fixture
def eval_questions() -> list[dict]:
    return json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))


@pytest.mark.asyncio
async def test_rag_retrieval_hits_expected_celex(eval_questions: list[dict]):
    """Each eval question should retrieve at least one chunk from expected CELEX."""
    rag = RagService()
    failures: list[str] = []
    for item in eval_questions:
        request = QueryRequest(question=item["question"], audience="professional")
        results = await rag._retrieve(request)
        retrieved_celex = {r.get("celex", "") for r in results}
        expected = set(item["expected_celex"])
        if not retrieved_celex.intersection(expected):
            failures.append(f"{item['question'][:50]}... -> got {sorted(retrieved_celex)[:5]}")
    assert not failures, "Retrieval misses:\n" + "\n".join(failures)

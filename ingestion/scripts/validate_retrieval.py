#!/usr/bin/env python3
"""Validate RAG retrieval against curated eval questions."""
import asyncio
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from backend.src.services.rag_service import RagService
from shared.schemas.query import QueryRequest

FIXTURE = Path(__file__).resolve().parents[2] / "backend/tests/fixtures/rag_eval_questions.json"


async def main() -> int:
    questions = json.loads(FIXTURE.read_text(encoding="utf-8"))
    rag = RagService()
    passed = 0
    failed = 0
    for item in questions:
        request = QueryRequest(question=item["question"], audience="professional")
        results = await rag._retrieve(request)
        retrieved = {r.get("celex", "") for r in results}
        expected = set(item["expected_celex"])
        hit = bool(retrieved.intersection(expected))
        status = "PASS" if hit else "FAIL"
        print(f"[{status}] {item['question'][:60]}")
        if not hit:
            print(f"       expected: {sorted(expected)}")
            print(f"       got: {sorted(retrieved)[:6]}")
            failed += 1
        else:
            passed += 1
    print(f"\nResult: {passed}/{len(questions)} passed")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))

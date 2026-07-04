#!/usr/bin/env python3
"""Debug hybrid retrieval, adequacy gate, and topic match for a query."""
from __future__ import annotations

import argparse
import asyncio
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from backend.src.services.context_adequacy_service import ContextAdequacyService
from backend.src.services.layperson_topic_service import LaypersonTopicService
from backend.src.services.retrieval_pipeline_service import RetrievalPipelineService
from shared.schemas.query import QueryRequest


def _chunk_summary(chunk: dict, index: int) -> dict:
    return {
        "rank": index + 1,
        "celex": chunk.get("celex", ""),
        "title": (chunk.get("title") or "")[:80],
        "score": round(float(chunk.get("score") or 0), 4),
        "rerank_score": round(float(chunk.get("rerank_score") or 0), 4),
        "preview": (chunk.get("text") or "")[:160],
    }


async def debug_query(question: str, top_k: int) -> dict:
    request = QueryRequest(question=question, audience="layperson", query_mode="open")
    pipeline = RetrievalPipelineService()
    chunks, route, explain = await pipeline.retrieve(request, session=None)
    trimmed = chunks[:top_k]
    adequacy = ContextAdequacyService().assess(question, trimmed, retrieval_route=route)
    topic = LaypersonTopicService().match(question)
    return {
        "question": question,
        "retrieval_route": route,
        "chunk_count": len(chunks),
        "top_chunks": [_chunk_summary(c, i) for i, c in enumerate(trimmed)],
        "adequacy": {
            "is_adequate": adequacy.is_adequate,
            "reason": adequacy.reason,
            "coverage_status": adequacy.coverage_status,
        },
        "topic_match": topic.topic_id if topic else None,
        "explainability": explain.model_dump(mode="json") if explain else {},
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Debug retrieval for a layperson query")
    parser.add_argument("--query", required=True, help="Question text")
    parser.add_argument("--top-k", type=int, default=10, help="Chunks to show")
    args = parser.parse_args()
    result = asyncio.run(debug_query(args.query, args.top_k))
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()

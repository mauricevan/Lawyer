#!/usr/bin/env python3
"""Purge and reingest lifecycle reindex candidates (plan13 AB)."""
import argparse
import asyncio
import json
import logging
from pathlib import Path

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from backend.src.config import settings
from backend.src.database import Base
from backend.src.services.document_reindex_service import DocumentReindexService, ReindexCandidate
from backend.src.utils.document_lifecycle_config import reindex_report_path
from ingestion.src.clients.cellar_rest_client import CellarRestClient
from ingestion.src.data.curated_loader import load_curated_documents
from ingestion.src.indexer import ingest_document
from ingestion.src.ingest_utils import purge_document_index

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

_REPO = Path(__file__).resolve().parents[2]


def _curated_lookup() -> dict[str, object]:
    return {f"{doc.celex}:{doc.language}": doc for doc in load_curated_documents()}


async def _reindex_candidate(
    candidate: ReindexCandidate,
    curated: dict[str, object],
    session,
    cellar: CellarRestClient,
) -> dict[str, str | int]:
    key = f"{candidate.celex}:{candidate.language}"
    metadata = curated.get(key)
    if metadata is None:
        return {"celex": candidate.celex, "language": candidate.language, "status": "skipped_not_curated"}
    await purge_document_index(candidate.celex, session, candidate.language)
    chunk_count = await ingest_document(metadata, session, use_live_fetch=True, cellar=cellar)
    if chunk_count == 0:
        return {"celex": candidate.celex, "language": candidate.language, "status": "failed_no_chunks"}
    return {
        "celex": candidate.celex,
        "language": candidate.language,
        "status": "reindexed",
        "chunks": chunk_count,
        "reason": candidate.reason,
    }


async def run_reindex(report_path: Path, delay_seconds: float) -> dict:
    engine = create_async_engine(settings.database_url)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    service = DocumentReindexService()
    session_factory = async_sessionmaker(engine, expire_on_commit=False)
    cellar = CellarRestClient(delay_seconds=delay_seconds)
    curated = _curated_lookup()

    async with session_factory() as session:
        candidates = await service.list_candidates(session)

    results: list[dict] = []
    async with session_factory() as session:
        for candidate in candidates:
            try:
                results.append(await _reindex_candidate(candidate, curated, session, cellar))
            except Exception as exc:
                logger.exception("Reindex failed for %s", candidate.celex)
                results.append(
                    {
                        "celex": candidate.celex,
                        "language": candidate.language,
                        "status": "failed",
                        "error": str(exc),
                    }
                )
                await session.rollback()

    sla = service.evaluate_sla(candidates)
    payload = {
        "suite": "lifecycle_reindex",
        "candidate_count": len(candidates),
        "reindexed": sum(1 for row in results if row.get("status") == "reindexed"),
        "failed": sum(1 for row in results if str(row.get("status", "")).startswith("failed")),
        "skipped": sum(1 for row in results if row.get("status") == "skipped_not_curated"),
        "sla": sla,
        "candidates": [
            {
                "celex": row.celex,
                "language": row.language,
                "reason": row.reason,
                "modified_at": row.modified_at.isoformat() if row.modified_at else None,
                "indexed_at": row.indexed_at.isoformat() if row.indexed_at else None,
            }
            for row in candidates
        ],
        "results": results,
    }
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    await engine.dispose()
    return payload


def main() -> None:
    parser = argparse.ArgumentParser(description="Lifecycle reindex for drift/stale docs")
    parser.add_argument("--report", type=Path, default=None)
    parser.add_argument("--delay-seconds", type=float, default=2.0)
    args = parser.parse_args()
    report = args.report or (_REPO / reindex_report_path())
    payload = asyncio.run(run_reindex(report, args.delay_seconds))
    print(json.dumps(payload, indent=2))
    if payload["failed"]:
        raise SystemExit(f"Lifecycle reindex failed for {payload['failed']} document(s)")


if __name__ == "__main__":
    main()

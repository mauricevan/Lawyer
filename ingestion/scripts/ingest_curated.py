#!/usr/bin/env python3
"""Ingest curated EUR-Lex documents with rate limiting and resume support."""
import argparse
import asyncio
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from backend.src.config import settings
from backend.src.database import Base
from ingestion.src.clients.cellar_rest_client import CellarRestClient
from ingestion.src.data.curated_loader import load_curated_documents
from ingestion.src.indexer import ingest_document
from ingestion.src.ingest_utils import (
    DEFAULT_FAILED_LOG,
    is_document_indexed,
    purge_document_index,
    write_failed_log,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DEFAULT_FORCE_CELEX = ["32024R1689"]


def _parse_force_list(raw: str | None) -> set[str]:
    if not raw:
        return set()
    return {item.strip() for item in raw.split(",") if item.strip()}


def _documents_from_offset(documents, from_celex: str | None):
    if not from_celex:
        return documents
    for index, document in enumerate(documents):
        if document.celex == from_celex:
            return documents[index:]
    logger.warning("CELEX %s not found; ingesting full list", from_celex)
    return documents


async def run_ingest(args: argparse.Namespace) -> dict[str, int]:
    engine = create_async_engine(settings.database_url)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    documents = _documents_from_offset(load_curated_documents(), args.from_celex)
    if args.limit:
        documents = documents[: args.limit]

    force_celex = _parse_force_list(args.force_celex)
    if args.force_ai_act:
        force_celex.update(DEFAULT_FORCE_CELEX)

    cellar = CellarRestClient(delay_seconds=args.delay_seconds)
    session_factory = async_sessionmaker(engine, expire_on_commit=False)

    stats = {"success": 0, "skipped": 0, "failed": 0, "chunks": 0}
    failures: list[dict[str, str]] = []

    async with session_factory() as session:
        for document in documents:
            celex = document.celex
            if celex in force_celex or args.force_reindex:
                await purge_document_index(celex, session)
            elif args.skip_existing and await is_document_indexed(celex, session):
                stats["skipped"] += 1
                logger.info("Skipping indexed document %s", celex)
                continue

            try:
                chunk_count = await ingest_document(
                    document, session, use_live_fetch=True, cellar=cellar
                )
                if chunk_count == 0:
                    stats["failed"] += 1
                    failures.append({"celex": celex, "error": "no_content_parsed"})
                    logger.warning("No chunks for %s", celex)
                else:
                    stats["success"] += 1
                    stats["chunks"] += chunk_count
            except Exception as exc:
                stats["failed"] += 1
                failures.append({"celex": celex, "error": str(exc)})
                await session.rollback()
                logger.exception("Failed to ingest %s", celex)

    if failures:
        log_path = write_failed_log(failures, Path(args.failed_log) if args.failed_log else None)
        logger.info("Wrote %d failures to %s", len(failures), log_path)
    await engine.dispose()
    return stats


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Ingest curated EUR-Lex corpus")
    parser.add_argument("--skip-existing", action="store_true", default=True)
    parser.add_argument("--no-skip-existing", action="store_false", dest="skip_existing")
    parser.add_argument("--from-celex", type=str, default=None, help="Resume from CELEX")
    parser.add_argument("--limit", type=int, default=None, help="Max documents to ingest")
    parser.add_argument("--delay-seconds", type=float, default=2.0, help="Delay between fetches")
    parser.add_argument("--force-celex", type=str, default=None, help="Comma-separated CELEX to re-index")
    parser.add_argument(
        "--force-ai-act",
        action="store_true",
        default=True,
        help="Re-index AI Act (32024R1689) with full live text",
    )
    parser.add_argument("--no-force-ai-act", action="store_false", dest="force_ai_act")
    parser.add_argument("--force-reindex", action="store_true", help="Purge and rebuild every document")
    parser.add_argument("--failed-log", type=str, default=str(DEFAULT_FAILED_LOG))
    return parser


async def main() -> None:
    args = _build_parser().parse_args()
    stats = await run_ingest(args)
    logger.info(
        "Ingest complete: success=%d skipped=%d failed=%d chunks=%d",
        stats["success"],
        stats["skipped"],
        stats["failed"],
        stats["chunks"],
    )


if __name__ == "__main__":
    asyncio.run(main())

#!/usr/bin/env python3
"""Ingest FR/DE/ES seed documents for multilingual eval (plan11 AA / EXP-001)."""
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
from ingestion.src.data.multilingual_loader import load_multilingual_seed_documents
from ingestion.src.indexer import ingest_document
from ingestion.src.ingest_utils import is_document_indexed, purge_document_index, write_failed_log

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def run_ingest(args: argparse.Namespace) -> dict[str, int]:
    engine = create_async_engine(settings.database_url)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    languages = tuple(item.strip() for item in args.languages.split(",") if item.strip())
    documents = load_multilingual_seed_documents(languages=languages)
    if args.celex:
        celex_filter = {item.strip() for item in args.celex.split(",") if item.strip()}
        documents = [doc for doc in documents if doc.celex in celex_filter]
    cellar = CellarRestClient(delay_seconds=args.delay_seconds)
    session_factory = async_sessionmaker(engine, expire_on_commit=False)

    stats = {"success": 0, "skipped": 0, "failed": 0, "chunks": 0}
    failures: list[dict[str, str]] = []

    async with session_factory() as session:
        for document in documents:
            key = f"{document.celex}:{document.language}"
            if args.force_reindex:
                await purge_document_index(document.celex, session, document.language)
            elif args.skip_existing and await is_document_indexed(
                document.celex, session, document.language
            ):
                stats["skipped"] += 1
                logger.info("Skipping indexed %s", key)
                continue
            try:
                count = await ingest_document(
                    document, session, use_live_fetch=True, cellar=cellar
                )
                if count == 0:
                    stats["failed"] += 1
                    failures.append({"celex": key, "error": "no_content_parsed"})
                else:
                    stats["success"] += 1
                    stats["chunks"] += count
            except Exception as exc:
                stats["failed"] += 1
                failures.append({"celex": key, "error": str(exc)})
                await session.rollback()
                logger.exception("Failed ingest %s", key)

    if failures:
        write_failed_log(failures)
    await engine.dispose()
    return stats


def main() -> None:
    parser = argparse.ArgumentParser(description="Ingest multilingual EUR-Lex seed")
    parser.add_argument("--languages", default="fr,de,es")
    parser.add_argument("--celex", default="", help="Comma-separated CELEX filter")
    parser.add_argument("--delay-seconds", type=float, default=2.0)
    parser.add_argument("--skip-existing", action="store_true", default=True)
    parser.add_argument("--no-skip-existing", action="store_false", dest="skip_existing")
    parser.add_argument("--force-reindex", action="store_true")
    args = parser.parse_args()
    stats = asyncio.run(run_ingest(args))
    logger.info(
        "Multilingual ingest: success=%d skipped=%d failed=%d chunks=%d",
        stats["success"],
        stats["skipped"],
        stats["failed"],
        stats["chunks"],
    )
    if stats["failed"]:
        sys.exit(1)


if __name__ == "__main__":
    main()

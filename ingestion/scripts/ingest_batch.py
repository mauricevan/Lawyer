#!/usr/bin/env python3
"""Batch ingestion script for scaling to 50K documents (no Celery required)."""
import asyncio
import argparse
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from backend.src.config import settings
from backend.src.database import Base
from ingestion.src.clients.sparql_client import SparqlClient
from ingestion.src.indexer import ingest_document
from shared.schemas.document import DocumentMetadata, VersionType

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BATCH_SIZE = 100


async def ingest_batch(offset: int, limit: int, use_sparql: bool) -> int:
    engine = create_async_engine(settings.database_url)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    session_factory = async_sessionmaker(engine, expire_on_commit=False)
    sparql = SparqlClient()
    total = 0
    async with session_factory() as session:
        if use_sparql:
            works = await sparql.fetch_works_page(offset=offset, limit=limit)
            for work in works:
                meta = DocumentMetadata(
                    celex=work.get("celex", ""),
                    cellar_id=None,
                    title=work.get("title", work.get("celex", "")),
                    language="nl",
                    version_type=VersionType.BASE,
                )
                if meta.celex:
                    total += await ingest_document(meta, session, use_live_fetch=True)
        else:
            from ingestion.src.data.seed_documents import SEED_DOCUMENTS
            for doc in SEED_DOCUMENTS[offset:offset + limit]:
                total += await ingest_document(doc, session, use_live_fetch=False)
    await engine.dispose()
    return total


async def main() -> None:
    parser = argparse.ArgumentParser(description="Batch ingest EUR-Lex documents")
    parser.add_argument("--offset", type=int, default=0)
    parser.add_argument("--limit", type=int, default=BATCH_SIZE)
    parser.add_argument("--sparql", action="store_true", help="Fetch metadata via SPARQL")
    args = parser.parse_args()
    count = await ingest_batch(args.offset, args.limit, args.sparql)
    logger.info("Batch complete: %d chunks indexed", count)


if __name__ == "__main__":
    asyncio.run(main())

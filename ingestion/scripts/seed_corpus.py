#!/usr/bin/env python3
"""Seed the prototype corpus with top-20 EUR-Lex documents."""
import asyncio
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from backend.src.config import settings
from backend.src.database import Base
from ingestion.src.data.seed_documents import SEED_DOCUMENTS
from ingestion.src.indexer import ingest_document

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def main() -> None:
    engine = create_async_engine(settings.database_url)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    session_factory = async_sessionmaker(engine, expire_on_commit=False)
    total_chunks = 0
    async with session_factory() as session:
        for doc_meta in SEED_DOCUMENTS:
            count = await ingest_document(doc_meta, session, use_live_fetch=True)
            total_chunks += count
    logger.info("Seed complete: %d documents, %d chunks", len(SEED_DOCUMENTS), total_chunks)
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())

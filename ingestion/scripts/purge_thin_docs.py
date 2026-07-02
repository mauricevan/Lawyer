#!/usr/bin/env python3
"""Purge documents with too few chunks so they can be fully re-indexed."""
import asyncio
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from backend.src.config import settings
from ingestion.src.ingest_utils import purge_document_index
from backend.src.models.tables import Chunk

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

MAX_CHUNKS = 3


async def main() -> None:
    engine = create_async_engine(settings.database_url)
    session_factory = async_sessionmaker(engine, expire_on_commit=False)
    async with session_factory() as session:
        rows = await session.execute(
            select(Chunk.celex, func.count(Chunk.id))
            .group_by(Chunk.celex)
            .having(func.count(Chunk.id) <= MAX_CHUNKS)
        )
        thin_celex = [row[0] for row in rows.all()]
        for celex in thin_celex:
            await purge_document_index(celex, session)
        logger.info("Purged %d thin documents (<= %d chunks)", len(thin_celex), MAX_CHUNKS)
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())

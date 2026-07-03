#!/usr/bin/env python3
"""Seed minimal offline corpus for CI integration eval (plan11 AD)."""
import asyncio
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from backend.src.config import settings
from backend.src.database import Base
from ingestion.src.data.curated_loader import load_curated_documents
from ingestion.src.indexer import ingest_document
from shared.schemas.document import DocumentMetadata

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

CI_PAIRS: tuple[tuple[str, str], ...] = (
    ("32016R0679", "nl"),
    ("32024R1689", "nl"),
    ("32022R2554", "nl"),
    ("32019L1152", "nl"),
    ("32003L0088", "nl"),
    ("32016R0679", "fr"),
    ("32024R1689", "fr"),
    ("32022R2554", "fr"),
    ("32016R0679", "de"),
    ("32024R1689", "de"),
    ("32022R2554", "de"),
    ("32016R0679", "es"),
    ("32024R1689", "es"),
    ("32022R2554", "es"),
)


def _resolve_metadata(celex: str, language: str) -> DocumentMetadata:
    for document in load_curated_documents():
        if document.celex == celex and document.language == language:
            return document
    for document in load_curated_documents():
        if document.celex == celex:
            return document.model_copy(update={"language": language})
    raise ValueError(f"No curated metadata for {celex}:{language}")


async def main() -> None:
    engine = create_async_engine(settings.database_url)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    session_factory = async_sessionmaker(engine, expire_on_commit=False)
    total = 0
    async with session_factory() as session:
        for celex, language in CI_PAIRS:
            metadata = _resolve_metadata(celex, language)
            count = await ingest_document(metadata, session, use_live_fetch=False)
            total += count
            logger.info("Seeded %s:%s (%d chunks)", celex, language, count)
    logger.info("CI seed complete: %d chunks", total)
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())

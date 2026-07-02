"""Backfill chunks.text from Qdrant payloads for PostgreSQL FTS."""
import asyncio
import logging

from sqlalchemy import update

from backend.src.database import SessionLocal, init_db
from backend.src.models.tables import Chunk
from backend.src.services.qdrant_service import QdrantService

logger = logging.getLogger(__name__)
BATCH_SIZE = 100


async def backfill() -> int:
    await init_db()
    qdrant = QdrantService()
    client = qdrant._client
    collection = qdrant._collection
    updated = 0
    offset = None
    async with SessionLocal() as session:
        while True:
            points, offset = client.scroll(
                collection_name=collection,
                limit=BATCH_SIZE,
                offset=offset,
                with_payload=True,
                with_vectors=False,
            )
            if not points:
                break
            for point in points:
                payload = point.payload or {}
                chunk_id = payload.get("chunk_id")
                text = payload.get("text")
                if not chunk_id or not text:
                    continue
                await session.execute(
                    update(Chunk)
                    .where(Chunk.chunk_id == chunk_id)
                    .values(text=str(text)[:8000])
                )
                updated += 1
            await session.commit()
            if offset is None:
                break
    logger.info("Backfilled %s chunk text rows", updated)
    return updated


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(backfill())

"""Helpers for curated batch ingestion."""
import json
import logging
from datetime import datetime, timezone
from pathlib import Path

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.src.models.tables import Chunk, Document
from backend.src.services.qdrant_service import QdrantService

logger = logging.getLogger(__name__)

FAILED_LOG_DIR = Path(__file__).resolve().parents[1] / "logs"
DEFAULT_FAILED_LOG = FAILED_LOG_DIR / "failed_celex.json"


async def is_document_indexed(celex: str, session: AsyncSession) -> bool:
    """Return True when the document has been indexed with at least one chunk."""
    result = await session.execute(
        select(Document).where(Document.celex == celex, Document.indexed_at.is_not(None))
    )
    document = result.scalar_one_or_none()
    if not document:
        return False
    chunk_count = await session.execute(
        select(Chunk.id).where(Chunk.document_id == document.id).limit(1)
    )
    return chunk_count.scalar_one_or_none() is not None


async def purge_document_index(celex: str, session: AsyncSession) -> None:
    """Remove chunks from PostgreSQL and Qdrant so a document can be re-indexed."""
    result = await session.execute(select(Document).where(Document.celex == celex))
    document = result.scalar_one_or_none()
    if document:
        await session.execute(delete(Chunk).where(Chunk.document_id == document.id))
        document.indexed_at = None
    QdrantService().delete_by_celex(celex)
    await session.commit()
    logger.info("Purged index for %s", celex)


def write_failed_log(failures: list[dict[str, str]], path: Path | None = None) -> Path:
    """Persist failed CELEX entries for retry."""
    target = path or DEFAULT_FAILED_LOG
    target.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "failures": failures,
    }
    target.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return target

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


async def is_document_indexed(
    celex: str,
    session: AsyncSession,
    language: str = "nl",
) -> bool:
    """Return True when the CELEX+language pair has indexed chunks."""
    result = await session.execute(
        select(Document).where(
            Document.celex == celex,
            Document.language == language,
            Document.indexed_at.is_not(None),
        )
    )
    document = result.scalar_one_or_none()
    if not document:
        return False
    chunk_count = await session.execute(
        select(Chunk.id).where(Chunk.document_id == document.id).limit(1)
    )
    return chunk_count.scalar_one_or_none() is not None


async def purge_document_index(
    celex: str,
    session: AsyncSession,
    language: str | None = None,
) -> None:
    """Remove chunks for CELEX, optionally scoped to one language."""
    query = select(Document).where(Document.celex == celex)
    if language:
        query = query.where(Document.language == language)
    result = await session.execute(query)
    documents = result.scalars().all()
    qdrant = QdrantService()
    for document in documents:
        chunk_rows = await session.execute(
            select(Chunk).where(Chunk.document_id == document.id)
        )
        for chunk in chunk_rows.scalars().all():
            qdrant.delete_by_chunk_id(chunk.chunk_id)
        await session.execute(delete(Chunk).where(Chunk.document_id == document.id))
        document.indexed_at = None
    if not language and not documents:
        qdrant.delete_by_celex(celex)
    await session.commit()
    scope = f"{celex}:{language}" if language else celex
    logger.info("Purged index for %s", scope)


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

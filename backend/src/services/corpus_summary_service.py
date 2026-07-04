"""Public corpus metadata for trust indicators (blueprint §7)."""
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.src.models.tables import Chunk, Document
from backend.src.services.qdrant_service import QdrantService


class CorpusSummaryService:
    """Builds non-sensitive corpus stats for the frontend provenance banner."""

    async def build_summary(self, session: AsyncSession) -> dict:
        doc_count = await session.scalar(select(func.count()).select_from(Document))
        chunk_count = await session.scalar(select(func.count()).select_from(Chunk))
        last_indexed = await session.scalar(select(func.max(Document.indexed_at)))
        qdrant_points = QdrantService().count_points()
        return {
            "documents_indexed": int(doc_count or 0),
            "chunks_indexed": int(chunk_count or 0),
            "vector_points": qdrant_points,
            "last_indexed_at": last_indexed.isoformat() if last_indexed else None,
        }

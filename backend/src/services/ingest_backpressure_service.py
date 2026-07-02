"""Backpressure checks before enqueueing ingest jobs."""
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.src.config import settings
from backend.src.models.tables import IngestionJob


class IngestBackpressureService:
    """Prevents ingest queue overload."""

    async def can_enqueue(self, session: AsyncSession) -> bool:
        pending = await session.execute(
            select(func.count())
            .select_from(IngestionJob)
            .where(IngestionJob.status.in_(("pending", "running")))
        )
        count = int(pending.scalar() or 0)
        return count < settings.ingest_queue_max_pending

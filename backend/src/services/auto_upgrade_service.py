"""Queue popular live-cache documents for curated ingest."""
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.src.models.tables import Document, IngestionJob
from backend.src.services.ingest_queue_service import IngestQueueService

AUTO_UPGRADE_HIT_THRESHOLD = 10


class AutoUpgradeService:
    """Promotes frequently requested CELEX documents to ingest queue."""

    def __init__(self) -> None:
        self._ingest_queue = IngestQueueService()

    async def maybe_queue(self, session: AsyncSession, celex: str, hit_count: int) -> bool:
        if hit_count < AUTO_UPGRADE_HIT_THRESHOLD:
            return False
        existing_doc = await session.execute(
            select(Document.id).where(Document.celex == celex).limit(1)
        )
        if existing_doc.scalar_one_or_none():
            return False
        pending_job = await session.execute(
            select(IngestionJob.id)
            .where(IngestionJob.celex == celex, IngestionJob.status.in_(("pending", "running")))
            .limit(1)
        )
        if pending_job.scalar_one_or_none():
            return False
        session.add(IngestionJob(celex=celex, status="pending", progress=0))
        await session.flush()
        await self._ingest_queue.enqueue_celex(celex, session=session)
        return True

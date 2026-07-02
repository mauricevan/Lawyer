"""Enqueue ingestion jobs to Celery workers with queue profiles."""
import logging

from sqlalchemy.ext.asyncio import AsyncSession

from backend.src.config import settings
from backend.src.services.ingest_backpressure_service import IngestBackpressureService
from ingestion.src.config.queue_profiles import PROFILE_QUEUES

logger = logging.getLogger(__name__)


class IngestQueueService:
    """Dispatches CELEX ingest tasks to background workers."""

    def __init__(self) -> None:
        self._backpressure = IngestBackpressureService()

    async def enqueue_celex(
        self,
        celex: str,
        session: AsyncSession | None = None,
        profile: str = "high",
    ) -> bool:
        if not settings.enable_celery_ingest:
            logger.info("Celery ingest disabled; skipped enqueue for %s", celex)
            return False
        if session is not None and not await self._backpressure.can_enqueue(session):
            logger.warning("Ingest backpressure active; skipped enqueue for %s", celex)
            return False
        try:
            self._dispatch(celex, profile)
            from backend.src.services.prometheus_exporter import INGEST_ENQUEUE_TOTAL

            INGEST_ENQUEUE_TOTAL.labels(result="queued").inc()
            return True
        except Exception as exc:
            logger.warning("Failed to enqueue ingest for %s: %s", celex, exc)
            try:
                from backend.src.services.prometheus_exporter import INGEST_ENQUEUE_TOTAL
                INGEST_ENQUEUE_TOTAL.labels(result="failed").inc()
            except Exception:
                pass
            return False

    def _dispatch(self, celex: str, profile: str) -> None:
        from ingestion.src.workers.ingest_tasks import ingest_single_document

        queue = PROFILE_QUEUES.get(profile, PROFILE_QUEUES["high"])
        ingest_single_document.apply_async(args=[celex, profile], queue=queue)

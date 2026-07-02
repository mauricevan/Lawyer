"""Celery tasks for document ingestion pipeline."""
import asyncio
import logging

from celery.exceptions import MaxRetriesExceededError

from ingestion.src.celery_app import celery_app
from ingestion.src.config.queue_profiles import PROFILE_QUEUES, QUEUE_DEAD_LETTER, QUEUE_RETRY
from ingestion.src.workers.ingest_runner import mark_dead_letter, run_celex_ingest

logger = logging.getLogger(__name__)


def _run_async(coro):
    return asyncio.run(coro)


@celery_app.task(bind=True, max_retries=3, name="ingestion.src.workers.ingest_tasks.ingest_single_document")
def ingest_single_document(self, celex: str, queue_profile: str = "high") -> dict:
    try:
        return _run_async(run_celex_ingest(celex, queue_profile=queue_profile))
    except Exception as exc:
        logger.error("Ingest failed for %s: %s", celex, exc)
        try:
            raise self.retry(exc=exc, countdown=60, queue=QUEUE_RETRY)
        except MaxRetriesExceededError:
            record_dead_letter.delay(celex, str(exc), queue_profile)
            raise


@celery_app.task(name="ingestion.src.workers.ingest_tasks.ingest_batch_celex")
def ingest_batch_celex(celex_list: list[str]) -> dict:
    queue = PROFILE_QUEUES["batch"]
    for celex in celex_list:
        ingest_single_document.apply_async(args=[celex, "batch"], queue=queue)
    return {"queued": len(celex_list)}


@celery_app.task(name="ingestion.src.workers.ingest_tasks.retry_failed_ingest")
def retry_failed_ingest(celex: str) -> dict:
    return ingest_single_document.apply_async(args=[celex, "retry"], queue=QUEUE_RETRY).get()


@celery_app.task(name="ingestion.src.workers.ingest_tasks.record_dead_letter")
def record_dead_letter(celex: str, error: str, queue_profile: str = "high") -> dict:
    _run_async(mark_dead_letter(celex, error, queue_profile))
    return {"celex": celex, "status": "dead_letter"}

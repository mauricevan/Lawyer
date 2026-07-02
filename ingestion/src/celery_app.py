"""Celery application with queue profiles for scaled ingestion."""
from celery import Celery
from kombu import Exchange, Queue

from backend.src.config import settings
from ingestion.src.config.queue_profiles import (
    QUEUE_BATCH,
    QUEUE_DEAD_LETTER,
    QUEUE_HIGH_PRIORITY,
    QUEUE_RETRY,
)

celery_app = Celery(
    "lawyer_ingestion",
    broker=settings.redis_url,
    backend=settings.redis_url,
)
default_exchange = Exchange("lawyer_ingest", type="direct")
celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    task_track_started=True,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
    task_default_queue=QUEUE_BATCH,
    task_queues=(
        Queue(QUEUE_HIGH_PRIORITY, default_exchange, routing_key=QUEUE_HIGH_PRIORITY),
        Queue(QUEUE_BATCH, default_exchange, routing_key=QUEUE_BATCH),
        Queue(QUEUE_RETRY, default_exchange, routing_key=QUEUE_RETRY),
        Queue(QUEUE_DEAD_LETTER, default_exchange, routing_key=QUEUE_DEAD_LETTER),
    ),
    task_routes={
        "ingestion.src.workers.ingest_tasks.ingest_single_document": {"queue": QUEUE_HIGH_PRIORITY},
        "ingestion.src.workers.ingest_tasks.ingest_batch_celex": {"queue": QUEUE_BATCH},
        "ingestion.src.workers.ingest_tasks.retry_failed_ingest": {"queue": QUEUE_RETRY},
        "ingestion.src.workers.ingest_tasks.record_dead_letter": {"queue": QUEUE_DEAD_LETTER},
    },
)
celery_app.autodiscover_tasks(["ingestion.src.workers"])

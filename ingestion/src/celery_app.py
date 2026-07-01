"""Celery application for bulk ingestion (fase 4+)."""
from celery import Celery

from backend.src.config import settings

celery_app = Celery(
    "lawyer_ingestion",
    broker=getattr(settings, "redis_url", "redis://localhost:6379/0"),
    backend=getattr(settings, "redis_url", "redis://localhost:6379/0"),
)
celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    task_track_started=True,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
)
celery_app.autodiscover_tasks(["ingestion.src.workers"])

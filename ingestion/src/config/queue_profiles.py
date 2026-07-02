"""Celery queue profile names for ingestion workers."""
QUEUE_HIGH_PRIORITY = "ingest_high"
QUEUE_BATCH = "ingest_batch"
QUEUE_RETRY = "ingest_retry"
QUEUE_DEAD_LETTER = "ingest_dlq"

PROFILE_QUEUES = {
    "high": QUEUE_HIGH_PRIORITY,
    "batch": QUEUE_BATCH,
    "retry": QUEUE_RETRY,
}

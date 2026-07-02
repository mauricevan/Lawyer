"""Run async ingest jobs from Celery workers."""
import logging

from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from backend.src.config import settings
from backend.src.models.tables import IngestionJob
from ingestion.src.data.seed_documents import SEED_DOCUMENTS
from ingestion.src.indexer import ingest_document
from shared.schemas.document import DocumentMetadata

logger = logging.getLogger(__name__)


async def run_celex_ingest(celex: str, queue_profile: str = "high") -> dict:
    engine = create_async_engine(settings.database_url)
    session_factory = async_sessionmaker(engine, expire_on_commit=False)
    meta = next((d for d in SEED_DOCUMENTS if d.celex == celex), None)
    if not meta:
        meta = DocumentMetadata(celex=celex, title=celex, language="nl")
    async with session_factory() as session:
        job = await _get_or_create_job(session, celex, queue_profile)
        try:
            count = await ingest_document(meta, session)
            job.status = "completed"
            job.progress = 100
            job.error_log = None
            await session.commit()
            return {"celex": celex, "chunks": count, "status": "completed"}
        except Exception as exc:
            job.status = "failed"
            job.error_log = str(exc)[:2000]
            await session.commit()
            raise
        finally:
            await engine.dispose()


async def mark_dead_letter(celex: str, error: str, queue_profile: str = "high") -> None:
    engine = create_async_engine(settings.database_url)
    session_factory = async_sessionmaker(engine, expire_on_commit=False)
    try:
        async with session_factory() as session:
            job = await _get_or_create_job(session, celex, queue_profile)
            job.status = "dead_letter"
            job.error_log = error[:2000]
            await session.commit()
    finally:
        await engine.dispose()
    logger.error("CELEX %s moved to dead-letter queue: %s", celex, error)


async def _get_or_create_job(session, celex: str, queue_profile: str) -> IngestionJob:
    existing = await session.execute(
        select(IngestionJob).where(
            IngestionJob.celex == celex,
            IngestionJob.status.in_(("pending", "running")),
        )
    )
    job = existing.scalar_one_or_none()
    if job is None:
        job = IngestionJob(celex=celex, status="running", progress=0, queue_profile=queue_profile)
        session.add(job)
    else:
        job.status = "running"
        job.queue_profile = queue_profile
    await session.flush()
    return job

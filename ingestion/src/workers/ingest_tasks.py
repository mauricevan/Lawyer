"""Celery tasks for document ingestion pipeline."""
import asyncio
import logging

from ingestion.src.celery_app import celery_app
from ingestion.src.data.seed_documents import SEED_DOCUMENTS
from ingestion.src.indexer import ingest_document
from shared.schemas.document import DocumentMetadata

logger = logging.getLogger(__name__)


def _run_async(coro):
    return asyncio.get_event_loop().run_until_complete(coro)


@celery_app.task(bind=True, max_retries=3)
def ingest_single_document(self, celex: str) -> dict:
    """Ingest one document by CELEX with checkpointing."""
    from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
    from backend.src.config import settings
    from backend.src.database import Base
    from backend.src.models.tables import IngestionJob

    async def _ingest():
        engine = create_async_engine(settings.database_url)
        session_factory = async_sessionmaker(engine, expire_on_commit=False)
        meta = next((d for d in SEED_DOCUMENTS if d.celex == celex), None)
        if not meta:
            meta = DocumentMetadata(celex=celex, title=celex, language="nl")
        async with session_factory() as session:
            job = IngestionJob(celex=celex, status="running")
            session.add(job)
            await session.commit()
            try:
                count = await ingest_document(meta, session)
                job.status = "completed"
                job.progress = 100
                await session.commit()
                return {"celex": celex, "chunks": count, "status": "completed"}
            except Exception as exc:
                job.status = "failed"
                job.error_log = str(exc)
                await session.commit()
                raise
            finally:
                await engine.dispose()

    try:
        return _run_async(_ingest())
    except Exception as exc:
        logger.error("Ingest failed for %s: %s", celex, exc)
        raise self.retry(exc=exc, countdown=60)


@celery_app.task
def ingest_batch_celex(celex_list: list[str]) -> dict:
    """Queue ingestion for a batch of CELEX numbers."""
    for celex in celex_list:
        ingest_single_document.delay(celex)
    return {"queued": len(celex_list)}

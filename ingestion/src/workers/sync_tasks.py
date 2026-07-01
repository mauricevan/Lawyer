"""Celery beat tasks for incremental EUR-Lex sync."""
import asyncio
import logging
from datetime import datetime, timezone

from ingestion.src.celery_app import celery_app
from ingestion.src.clients.sparql_client import SparqlClient
from ingestion.src.workers.ingest_tasks import ingest_single_document

logger = logging.getLogger(__name__)


@celery_app.task
def delta_sync() -> dict:
    """Fetch documents modified since last sync cursor."""
    return asyncio.get_event_loop().run_until_complete(_delta_sync())


async def _delta_sync() -> dict:
    from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
    from sqlalchemy import select
    from backend.src.config import settings
    from backend.src.models.tables import SyncCursor

    engine = create_async_engine(settings.database_url)
    session_factory = async_sessionmaker(engine, expire_on_commit=False)
    sparql = SparqlClient()
    synced = 0
    async with session_factory() as session:
        result = await session.execute(
            select(SyncCursor).where(SyncCursor.source == "sparql_delta")
        )
        cursor = result.scalar_one_or_none()
        since = cursor.last_modified.strftime("%Y-%m-%d") if cursor and cursor.last_modified else "2020-01-01"
        offset = cursor.offset if cursor else 0
        works = await sparql.fetch_modified_since(since, offset=offset, limit=100)
        for work in works:
            celex = work.get("celex", "")
            if celex:
                ingest_single_document.delay(celex)
                synced += 1
        if cursor:
            cursor.offset = offset + len(works)
            cursor.last_modified = datetime.now(timezone.utc)
        else:
            session.add(SyncCursor(
                source="sparql_delta",
                last_modified=datetime.now(timezone.utc),
                offset=len(works),
            ))
        await session.commit()
    await engine.dispose()
    logger.info("Delta sync queued %d documents", synced)
    return {"queued": synced, "since": since}


celery_app.conf.beat_schedule = {
    "daily-delta-sync": {
        "task": "ingestion.src.workers.sync_tasks.delta_sync",
        "schedule": 86400.0,
    },
}

"""Admin dashboard API — ingestion stats and sync status."""
from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.src.database import SessionLocal
from backend.src.models.tables import Document, IngestionJob, QueryLog
from backend.src.services.qdrant_service import QdrantService

router = APIRouter(prefix="/admin", tags=["admin"])


async def get_db() -> AsyncSession:
    async with SessionLocal() as session:
        yield session


@router.get("/stats")
async def get_stats(session: AsyncSession = Depends(get_db)) -> dict:
    doc_count = await session.execute(select(func.count()).select_from(Document))
    job_result = await session.execute(
        select(IngestionJob.status, func.count())
        .group_by(IngestionJob.status)
    )
    query_count = await session.execute(select(func.count()).select_from(QueryLog))
    qdrant = QdrantService()
    return {
        "documents_indexed": doc_count.scalar() or 0,
        "vector_points": qdrant.count_points(),
        "queries_total": query_count.scalar() or 0,
        "ingestion_jobs": {row[0]: row[1] for row in job_result.all()},
    }


@router.get("/ingestion-jobs")
async def list_ingestion_jobs(
    session: AsyncSession = Depends(get_db),
    limit: int = 50,
) -> list[dict]:
    result = await session.execute(
        select(IngestionJob).order_by(IngestionJob.created_at.desc()).limit(limit)
    )
    jobs = result.scalars().all()
    return [
        {
            "id": str(j.id),
            "celex": j.celex,
            "status": j.status,
            "progress": j.progress,
            "error_log": j.error_log,
            "created_at": j.created_at.isoformat(),
        }
        for j in jobs
    ]

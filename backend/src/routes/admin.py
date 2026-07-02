"""Admin dashboard API — ingestion stats and sync status."""
from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.src.config import settings
from backend.src.database import SessionLocal
from backend.src.models.tables import AuditLog, Document, IngestionJob, LiveCache, QueryLog
from backend.src.services.metrics_service import metrics_service
from backend.src.services.qdrant_service import QdrantService
from backend.src.services.cache_cleanup_service import CacheCleanupService
from backend.src.services.feature_flag_service import FeatureFlagService
from backend.src.dependencies.auth import require_permission
from backend.src.security.rbac_matrix import Permission
from backend.src.services.redis_cache_service import RedisCacheService

router = APIRouter(prefix="/admin", tags=["admin"])
redis_cache = RedisCacheService()
cache_cleanup = CacheCleanupService()
feature_flags = FeatureFlagService()


async def get_db() -> AsyncSession:
    async with SessionLocal() as session:
        yield session


@router.get("/stats", dependencies=[Depends(require_permission(Permission.ADMIN_READ))])
async def get_stats(session: AsyncSession = Depends(get_db)) -> dict:
    doc_count = await session.execute(select(func.count()).select_from(Document))
    job_result = await session.execute(
        select(IngestionJob.status, func.count())
        .group_by(IngestionJob.status)
    )
    dead_letter_count = await session.execute(
        select(func.count()).select_from(IngestionJob).where(IngestionJob.status == "dead_letter")
    )
    query_count = await session.execute(select(func.count()).select_from(QueryLog))
    cache_count = await session.execute(select(func.count()).select_from(LiveCache))
    audit_count = await session.execute(select(func.count()).select_from(AuditLog))
    cache_hits = await session.execute(select(func.coalesce(func.sum(LiveCache.hit_count), 0)))
    qdrant = QdrantService()
    return {
        "documents_indexed": doc_count.scalar() or 0,
        "vector_points": qdrant.count_points(),
        "queries_total": query_count.scalar() or 0,
        "live_cache_entries": cache_count.scalar() or 0,
        "live_cache_hits_total": cache_hits.scalar() or 0,
        "audit_events_total": audit_count.scalar() or 0,
        "runtime_metrics": metrics_service.snapshot(),
        "feature_flags": {
            "live_fallback": feature_flags.is_live_fallback_enabled(),
            "hybrid_rrf": feature_flags.is_hybrid_rrf_enabled(),
            "auto_upgrade": feature_flags.is_auto_upgrade_enabled(),
            "audit_logging": feature_flags.is_audit_logging_enabled(),
        },
        "ingestion_jobs": {row[0]: row[1] for row in job_result.all()},
        "ingestion_dead_letter_total": dead_letter_count.scalar() or 0,
    }


@router.get("/ingestion-jobs", dependencies=[Depends(require_permission(Permission.ADMIN_READ))])
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


@router.get("/cache", dependencies=[Depends(require_permission(Permission.ADMIN_READ))])
async def get_cache_status(session: AsyncSession = Depends(get_db)) -> dict:
    redis_health = await redis_cache.health()
    now_utc = func.now()
    total = await session.execute(select(func.count()).select_from(LiveCache))
    active = await session.execute(
        select(func.count()).select_from(LiveCache).where(LiveCache.expires_at > now_utc)
    )
    expired = await session.execute(
        select(func.count()).select_from(LiveCache).where(LiveCache.expires_at <= now_utc)
    )
    top_cached = await session.execute(
        select(LiveCache.celex, func.sum(LiveCache.hit_count).label("hits"))
        .group_by(LiveCache.celex)
        .order_by(func.sum(LiveCache.hit_count).desc())
        .limit(5)
    )
    return {
        "redis": {
            **redis_health,
            "url": settings.redis_url if settings.enable_redis_cache else None,
        },
        "live_cache": {
            "total_entries": total.scalar() or 0,
            "active_entries": active.scalar() or 0,
            "expired_entries": expired.scalar() or 0,
            "top_celex": [
                {"celex": row[0], "hits": int(row[1] or 0)}
                for row in top_cached.all()
            ],
        },
    }


@router.post("/cache/cleanup", dependencies=[Depends(require_permission(Permission.ADMIN_WRITE))])
async def cleanup_expired_cache(session: AsyncSession = Depends(get_db)) -> dict[str, int]:
    removed = await cache_cleanup.purge_expired(session)
    return {"removed_entries": removed}


@router.get("/metrics", dependencies=[Depends(require_permission(Permission.ADMIN_READ))])
async def get_runtime_metrics() -> dict:
    return metrics_service.snapshot()

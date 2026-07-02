"""Health and readiness endpoints."""
from fastapi import APIRouter, Response
from sqlalchemy import text

from backend.src.config import settings
from backend.src.database import SessionLocal
from backend.src.services.prometheus_exporter import export_prometheus
from backend.src.services.qdrant_service import QdrantService
from backend.src.services.redis_cache_service import RedisCacheService

router = APIRouter(tags=["health"])
redis_cache = RedisCacheService()


@router.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/ready")
async def ready() -> dict[str, object]:
    checks: dict[str, object] = {}
    checks["postgres"] = await _check_postgres()
    checks["redis"] = await redis_cache.health() if settings.enable_redis_cache else {"status": "disabled"}
    checks["qdrant"] = _check_qdrant()
    is_ready = checks["postgres"] == "ok" and checks["qdrant"] == "ok"
    if settings.enable_redis_cache and checks["redis"].get("status") != "ok":
        is_ready = False
    return {"status": "ready" if is_ready else "degraded", "checks": checks}


@router.get("/metrics")
async def prometheus_metrics() -> Response:
    payload, content_type = export_prometheus()
    return Response(content=payload, media_type=content_type)


async def _check_postgres() -> str:
    try:
        async with SessionLocal() as session:
            await session.execute(text("SELECT 1"))
        return "ok"
    except Exception:
        return "error"


def _check_qdrant() -> str:
    try:
        QdrantService().count_points()
        return "ok"
    except Exception:
        return "error"

"""Health and readiness endpoints (plan14 AA)."""
from fastapi import APIRouter, Response
from starlette import status

from backend.src.services.prometheus_exporter import export_prometheus
from backend.src.services.readiness_service import ReadinessService

router = APIRouter(tags=["health"])
_readiness = ReadinessService()


@router.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/ready")
async def ready(response: Response) -> dict[str, object]:
    report = await _readiness.build_report()
    if report["status"] != "ready":
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    return report


@router.get("/metrics")
async def prometheus_metrics() -> Response:
    payload, content_type = export_prometheus()
    return Response(content=payload, media_type=content_type)

"""Admin audit trail endpoints (read-only for analysts)."""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from backend.src.database import SessionLocal
from backend.src.dependencies.auth import require_permission
from backend.src.security.rbac_matrix import Permission
from backend.src.services.audit_query_service import AuditQueryService
from backend.src.services.audit_retention_service import AuditRetentionService

router = APIRouter(prefix="/admin/audit", tags=["admin-audit"])
audit_query = AuditQueryService()
audit_retention = AuditRetentionService()


async def get_db() -> AsyncSession:
    async with SessionLocal() as session:
        yield session


@router.get("/logs")
async def list_audit_logs(
    session: AsyncSession = Depends(get_db),
    limit: int = 50,
    offset: int = 0,
    _principal=Depends(require_permission(Permission.ADMIN_READ)),
) -> dict:
    logs = await audit_query.list_logs(session, limit=limit, offset=offset)
    return {"items": logs, "limit": min(max(limit, 1), 200), "offset": max(offset, 0)}


@router.get("/completeness")
async def audit_completeness(
    session: AsyncSession = Depends(get_db),
    sample_size: int = 100,
    _principal=Depends(require_permission(Permission.ADMIN_READ)),
) -> dict:
    return await audit_query.completeness_sample(session, sample_size=sample_size)


@router.get("/report/monthly")
async def monthly_audit_report(
    session: AsyncSession = Depends(get_db),
    _principal=Depends(require_permission(Permission.ADMIN_READ)),
) -> dict:
    return await audit_query.monthly_report(session)


@router.get("/retention")
async def audit_retention_status(
    session: AsyncSession = Depends(get_db),
    _principal=Depends(require_permission(Permission.ADMIN_READ)),
) -> dict:
    return {
        "retention_days": audit_retention.retention_days(),
        "expired_pending_purge": await audit_retention.count_expired(session),
    }


@router.post("/retention/purge")
async def purge_expired_audit_logs(
    session: AsyncSession = Depends(get_db),
    _principal=Depends(require_permission(Permission.ADMIN_WRITE)),
) -> dict[str, int]:
    removed = await audit_retention.purge_expired(session)
    return {"removed_entries": removed}

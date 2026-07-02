"""Admin data lifecycle and retention endpoints."""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from backend.src.config import settings
from backend.src.database import SessionLocal
from backend.src.dependencies.auth import require_permission
from backend.src.security.data_classification import classification_report
from backend.src.security.rbac_matrix import Permission
from backend.src.services.data_retention_service import DataRetentionService

router = APIRouter(prefix="/admin/retention", tags=["admin-retention"])
data_retention = DataRetentionService()


async def get_db() -> AsyncSession:
    async with SessionLocal() as session:
        yield session


@router.get("/policy")
async def retention_policy(
    _principal=Depends(require_permission(Permission.ADMIN_READ)),
) -> dict:
    return {
        "query_log_retention_days": data_retention.query_log_retention_days(),
        "feedback_retention_days": data_retention.feedback_retention_days(),
        "conversation_retention_days": data_retention.conversation_retention_days(),
        "audit_retention_days": settings.audit_retention_days,
        "saved_conversations_exempt": True,
        "classification": classification_report(),
    }


@router.get("/status")
async def retention_status(
    session: AsyncSession = Depends(get_db),
    _principal=Depends(require_permission(Permission.ADMIN_READ)),
) -> dict:
    return {"expired_pending_purge": await data_retention.count_expired(session)}


@router.post("/purge")
async def purge_expired_data(
    session: AsyncSession = Depends(get_db),
    _principal=Depends(require_permission(Permission.ADMIN_WRITE)),
) -> dict[str, int]:
    return await data_retention.purge_expired(session)

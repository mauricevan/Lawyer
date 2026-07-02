"""Retention enforcement for audit log rows."""
from datetime import datetime, timedelta, timezone

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.src.config import settings
from backend.src.models.tables import AuditLog


class AuditRetentionService:
    """Purges audit events older than the configured retention window."""

    def retention_days(self) -> int:
        return max(settings.audit_retention_days, 1)

    def cutoff(self, now: datetime | None = None) -> datetime:
        current = now or datetime.now(timezone.utc)
        return current - timedelta(days=self.retention_days())

    async def purge_expired(self, session: AsyncSession) -> int:
        cutoff = self.cutoff()
        result = await session.execute(delete(AuditLog).where(AuditLog.created_at < cutoff))
        await session.commit()
        return int(result.rowcount or 0)

    async def count_expired(self, session: AsyncSession) -> int:
        cutoff = self.cutoff()
        result = await session.execute(
            select(AuditLog.id).where(AuditLog.created_at < cutoff)
        )
        return len(result.scalars().all())

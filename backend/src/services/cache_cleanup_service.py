"""Cleanup tasks for expired live_cache rows."""
from datetime import datetime, timezone

from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession

from backend.src.models.tables import LiveCache


class CacheCleanupService:
    """Removes expired persistent cache entries."""

    async def purge_expired(self, session: AsyncSession) -> int:
        now = datetime.now(timezone.utc)
        result = await session.execute(
            delete(LiveCache).where(
                LiveCache.expires_at.is_not(None),
                LiveCache.expires_at <= now,
            )
        )
        await session.commit()
        return int(result.rowcount or 0)

    async def purge_contaminated(self, session: AsyncSession) -> int:
        result = await session.execute(
            delete(LiveCache).where(LiveCache.chunk_text.ilike("%misschien%"))
        )
        await session.commit()
        return int(result.rowcount or 0)

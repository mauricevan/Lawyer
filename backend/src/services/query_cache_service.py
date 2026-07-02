"""In-memory and persistent retrieval cache helpers."""
import hashlib
from datetime import datetime, timedelta, timezone
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.src.config import settings
from backend.src.models.tables import LiveCache
from backend.src.services.auto_upgrade_service import AutoUpgradeService
from backend.src.services.feature_flag_service import FeatureFlagService
from backend.src.services.metrics_service import metrics_service
from backend.src.services.redis_cache_service import RedisCacheService


class QueryCacheService:
    """Caches retrieval outputs and tracks persistent live-cache entries."""

    def __init__(self) -> None:
        self._memory: dict[str, tuple[datetime, list[dict[str, Any]]]] = {}
        self._redis = RedisCacheService()
        self._auto_upgrade = AutoUpgradeService()
        self._flags = FeatureFlagService()

    def build_key(self, question: str, language: str, in_force_only: bool) -> str:
        raw = f"{question.strip().lower()}|{language}|{in_force_only}"
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()

    async def get(self, key: str) -> list[dict[str, Any]] | None:
        redis_value = await self._redis.get(key)
        if redis_value:
            self._memory[key] = (datetime.now(timezone.utc), redis_value)
            return redis_value
        item = self._memory.get(key)
        if not item:
            return None
        created_at, payload = item
        ttl = timedelta(seconds=settings.retrieval_cache_ttl_seconds)
        if datetime.now(timezone.utc) - created_at > ttl:
            self._memory.pop(key, None)
            return None
        return payload

    async def set(self, key: str, payload: list[dict[str, Any]]) -> None:
        self._memory[key] = (datetime.now(timezone.utc), payload)
        await self._redis.set(key, payload, ttl_seconds=settings.retrieval_cache_ttl_seconds)

    async def track_live_chunks(
        self,
        session: AsyncSession,
        query_hash: str,
        chunks: list[dict[str, Any]],
    ) -> None:
        expires_at = datetime.now(timezone.utc) + timedelta(seconds=settings.retrieval_cache_ttl_seconds)
        for chunk in chunks:
            celex = chunk.get("celex")
            if not celex:
                continue
            current = await session.execute(
                select(LiveCache).where(
                    LiveCache.query_hash == query_hash,
                    LiveCache.celex == celex,
                )
            )
            row = current.scalar_one_or_none()
            if row:
                row.hit_count += 1
                row.expires_at = expires_at
                await self._maybe_queue_upgrade(session, celex, row.hit_count)
                continue
            session.add(LiveCache(
                query_hash=query_hash,
                celex=celex,
                chunk_text=chunk.get("text", "")[:4000],
                qdrant_id=chunk.get("chunk_id"),
                hit_count=1,
                expires_at=expires_at,
            ))

    async def get_persisted_chunks(
        self,
        session: AsyncSession,
        query_hash: str,
    ) -> list[dict[str, Any]]:
        now = datetime.now(timezone.utc)
        result = await session.execute(
            select(LiveCache).where(
                LiveCache.query_hash == query_hash,
                LiveCache.expires_at.is_not(None),
                LiveCache.expires_at > now,
            )
        )
        rows = list(result.scalars().all())
        if not rows:
            return []
        for row in rows:
            row.hit_count += 1
            row.expires_at = now + timedelta(seconds=settings.retrieval_cache_ttl_seconds)
            await self._maybe_queue_upgrade(session, row.celex, row.hit_count)
        return [self._row_to_chunk(row) for row in rows]

    def _row_to_chunk(self, row: LiveCache) -> dict[str, Any]:
        return {
            "chunk_id": row.qdrant_id or f"cache:{row.celex}",
            "celex": row.celex,
            "title": f"Cached EUR-Lex {row.celex}",
            "text": row.chunk_text,
            "article_number": None,
            "language": "nl",
            "is_consolidated": False,
            "is_in_force": True,
            "score": 0.9,
            "source": "cache",
        }

    async def _maybe_queue_upgrade(
        self,
        session: AsyncSession,
        celex: str,
        hit_count: int,
    ) -> None:
        if not self._flags.is_auto_upgrade_enabled():
            return
        queued = await self._auto_upgrade.maybe_queue(session, celex, hit_count)
        if queued:
            metrics_service.record_auto_upgrade()

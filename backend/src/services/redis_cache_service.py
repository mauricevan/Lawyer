"""Redis-backed cache storage for retrieval results."""
import json
import logging
from typing import Any

from backend.src.config import settings

logger = logging.getLogger(__name__)


class RedisCacheService:
    """Thin async Redis wrapper with graceful failure mode."""

    def __init__(self) -> None:
        self._client = None
        self._disabled = not settings.enable_redis_cache

    async def get(self, key: str) -> list[dict[str, Any]] | None:
        if self._disabled:
            return None
        client = await self._get_client()
        if client is None:
            return None
        try:
            value = await client.get(key)
            if not value:
                return None
            decoded = json.loads(value)
            if isinstance(decoded, list):
                return decoded
            return None
        except Exception as exc:
            logger.warning("Redis GET failed for key %s: %s", key[:12], exc)
            return None

    async def set(self, key: str, payload: list[dict[str, Any]], ttl_seconds: int) -> None:
        if self._disabled:
            return
        client = await self._get_client()
        if client is None:
            return
        try:
            await client.set(key, json.dumps(payload), ex=ttl_seconds)
        except Exception as exc:
            logger.warning("Redis SET failed for key %s: %s", key[:12], exc)

    async def _get_client(self):
        if self._client is not None:
            return self._client
        try:
            from redis import asyncio as redis_asyncio
            self._client = redis_asyncio.from_url(
                settings.redis_url,
                decode_responses=True,
                socket_connect_timeout=0.5,
                socket_timeout=0.5,
            )
            await self._client.ping()
            return self._client
        except Exception as exc:
            logger.warning("Redis unavailable, using local cache only: %s", exc)
            self._disabled = True
            self._client = None
            return None

    async def health(self) -> dict[str, object]:
        if self._disabled:
            return {"enabled": False, "healthy": False}
        client = await self._get_client()
        if client is None:
            return {"enabled": True, "healthy": False}
        try:
            pong = await client.ping()
            return {"enabled": True, "healthy": bool(pong)}
        except Exception:
            return {"enabled": True, "healthy": False}

    async def flush_retrieval_keys(self) -> int:
        if self._disabled:
            return 0
        client = await self._get_client()
        if client is None:
            return 0
        try:
            removed = 0
            async for key in client.scan_iter(match="*"):
                await client.delete(key)
                removed += 1
            return removed
        except Exception as exc:
            logger.warning("Redis flush failed: %s", exc)
            return 0

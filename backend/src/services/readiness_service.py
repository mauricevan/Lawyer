"""Dependency readiness checks for /ready and admin (plan14 AA)."""
from typing import Any

from sqlalchemy import text

from backend.src.config import settings
from backend.src.database import SessionLocal
from backend.src.services.metrics_service import metrics_service
from backend.src.services.prometheus_exporter import sync_readiness_metrics
from backend.src.services.qdrant_service import QdrantService
from backend.src.services.redis_cache_service import RedisCacheService
from backend.src.utils.readiness_config import load_readiness_policy


class ReadinessService:
    """Verifies Tier-1/Tier-2 dependencies for readiness probes."""

    def __init__(
        self,
        redis_cache: RedisCacheService | None = None,
        qdrant: QdrantService | None = None,
    ) -> None:
        self._redis = redis_cache or RedisCacheService()
        self._qdrant = qdrant or QdrantService()
        self._policy = load_readiness_policy()

    async def run_checks(self) -> dict[str, dict[str, Any]]:
        return {
            "postgres": await self._check_postgres(),
            "qdrant": self._check_qdrant(),
            "redis": await self._check_redis(),
        }

    async def build_report(self, record_metric: bool = True) -> dict[str, Any]:
        report = await self.snapshot()
        if record_metric:
            metrics_service.record_readiness_check(report["status"] == "ready")
            report["metrics"] = metrics_service.readiness_snapshot()
        return report

    async def snapshot(self) -> dict[str, Any]:
        checks = await self.run_checks()
        is_ready = self.is_ready(checks)
        sync_readiness_metrics(checks, is_ready)
        return {
            "status": "ready" if is_ready else "degraded",
            "checks": checks,
            "tier1_ok": self._tier_status(checks, tier=1),
            "metrics": metrics_service.readiness_snapshot(),
        }

    def is_ready(self, checks: dict[str, dict[str, Any]]) -> bool:
        for name, config in self._policy.get("dependencies", {}).items():
            if not config.get("required_for_ready", False):
                continue
            if checks.get(name, {}).get("status") != "ok":
                return False
        return True

    def summarize_admin(self, report: dict[str, Any]) -> dict[str, Any]:
        checks = report.get("checks", {})
        return {
            "status": report.get("status"),
            "tier1_ok": report.get("tier1_ok"),
            "dependencies": checks,
            "pass_rate": report.get("metrics", {}).get("pass_rate"),
            "checks_total": report.get("metrics", {}).get("checks_total"),
        }

    async def _check_postgres(self) -> dict[str, Any]:
        base = self._dependency_meta("postgres")
        try:
            async with SessionLocal() as session:
                await session.execute(text("SELECT 1"))
            return {**base, "status": "ok"}
        except Exception as exc:
            return {**base, "status": "error", "error": exc.__class__.__name__}

    def _check_qdrant(self) -> dict[str, Any]:
        base = self._dependency_meta("qdrant")
        health = self._qdrant.health_check()
        if not health.get("healthy"):
            return {**base, "status": "error", "error": health.get("error", "unavailable")}
        return {**base, "status": "ok", "points_count": health.get("points_count", 0)}

    async def _check_redis(self) -> dict[str, Any]:
        base = self._dependency_meta("redis")
        if not settings.enable_redis_cache:
            return {**base, "status": "disabled", "enabled": False}
        health = await self._redis.health()
        if health.get("healthy"):
            return {**base, "status": "ok", "enabled": True}
        return {**base, "status": "error", "enabled": True}

    def _dependency_meta(self, name: str) -> dict[str, Any]:
        config = self._policy.get("dependencies", {}).get(name, {})
        return {
            "tier": config.get("tier", 2),
            "required_for_ready": bool(config.get("required_for_ready", False)),
            "fallback": config.get("fallback"),
        }

    def _tier_status(self, checks: dict[str, dict[str, Any]], tier: int) -> bool:
        for name, config in self._policy.get("dependencies", {}).items():
            if config.get("tier") != tier:
                continue
            if checks.get(name, {}).get("status") != "ok":
                return False
        return True

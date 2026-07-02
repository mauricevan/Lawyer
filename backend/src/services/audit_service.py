"""Audit trail service for query execution events."""
from sqlalchemy.ext.asyncio import AsyncSession

from backend.src.models.tables import AuditLog
from backend.src.services.feature_flag_service import FeatureFlagService


class AuditService:
    """Stores minimal compliant audit entries."""

    def __init__(self) -> None:
        self._flags = FeatureFlagService()

    async def log_query(
        self,
        session: AsyncSession,
        request_id: str,
        conversation_id: str | None,
        question: str,
        route: dict | None,
        chunk_ids: list[str] | None,
        latency_ms: int | None,
    ) -> None:
        if not self._flags.is_audit_logging_enabled():
            return
        from backend.src.config import settings

        session.add(AuditLog(
            request_id=request_id,
            conversation_id=conversation_id,
            question=question[:2000],
            route=route,
            chunk_ids=chunk_ids,
            model=settings.openrouter_model if settings.llm_provider == "openrouter" else "anthropic",
            latency_ms=latency_ms,
        ))

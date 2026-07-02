"""Read-only audit log queries and monthly reporting."""
from datetime import datetime, timezone

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.src.models.tables import AuditLog
from backend.src.services.audit_completeness_service import summarize_completeness


class AuditQueryService:
    """Lists audit events and builds governance reports."""

    async def list_logs(
        self,
        session: AsyncSession,
        limit: int = 50,
        offset: int = 0,
    ) -> list[dict]:
        bounded_limit = min(max(limit, 1), 200)
        result = await session.execute(
            select(AuditLog)
            .order_by(AuditLog.created_at.desc())
            .offset(max(offset, 0))
            .limit(bounded_limit)
        )
        return [self._serialize(entry) for entry in result.scalars().all()]

    async def completeness_sample(
        self,
        session: AsyncSession,
        sample_size: int = 100,
    ) -> dict:
        bounded = min(max(sample_size, 1), 200)
        result = await session.execute(
            select(AuditLog).order_by(AuditLog.created_at.desc()).limit(bounded)
        )
        return summarize_completeness(list(result.scalars().all()))

    async def monthly_report(self, session: AsyncSession) -> dict:
        month_start = datetime.now(timezone.utc).replace(
            day=1, hour=0, minute=0, second=0, microsecond=0
        )
        result = await session.execute(
            select(AuditLog).where(AuditLog.created_at >= month_start)
        )
        entries = list(result.scalars().all())
        completeness = summarize_completeness(entries)
        route_counts = self._count_routes(entries)
        latency = await self._latency_summary(session, month_start)
        return {
            "period_start": month_start.isoformat(),
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "totals": {
                "events": len(entries),
                "unique_conversations": len({e.conversation_id for e in entries if e.conversation_id}),
            },
            "completeness": completeness,
            "routes": route_counts,
            "latency_ms": latency,
        }

    async def _latency_summary(self, session: AsyncSession, since: datetime) -> dict[str, float | int]:
        result = await session.execute(
            select(
                func.count(AuditLog.id),
                func.avg(AuditLog.latency_ms),
                func.max(AuditLog.latency_ms),
            ).where(AuditLog.created_at >= since, AuditLog.latency_ms.is_not(None))
        )
        count, avg_ms, max_ms = result.one()
        return {
            "count": int(count or 0),
            "avg": round(float(avg_ms or 0.0), 2),
            "max": int(max_ms or 0),
        }

    def _count_routes(self, entries: list[AuditLog]) -> dict[str, int]:
        counts: dict[str, int] = {}
        for entry in entries:
            route = entry.route if isinstance(entry.route, dict) else {}
            label = str(route.get("retrieval_route", "unknown"))
            counts[label] = counts.get(label, 0) + 1
        return counts

    def _serialize(self, entry: AuditLog) -> dict:
        return {
            "id": str(entry.id),
            "request_id": entry.request_id,
            "conversation_id": entry.conversation_id,
            "question": entry.question[:200],
            "route": entry.route,
            "chunk_count": len(entry.chunk_ids or []),
            "model": entry.model,
            "latency_ms": entry.latency_ms,
            "created_at": entry.created_at.isoformat() if entry.created_at else None,
        }

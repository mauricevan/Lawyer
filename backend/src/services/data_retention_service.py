"""Retention enforcement for user-facing and operational data tables."""
from datetime import datetime, timedelta, timezone

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.src.config import settings
from backend.src.models.tables import Conversation, Message, QueryFeedback, QueryLog


class DataRetentionService:
    """Purges expired rows according to configured retention windows."""

    def query_log_retention_days(self) -> int:
        return max(settings.query_log_retention_days, 1)

    def feedback_retention_days(self) -> int:
        return max(settings.feedback_retention_days, 1)

    def conversation_retention_days(self) -> int:
        return max(settings.conversation_retention_days, 1)

    def cutoff(self, days: int, now: datetime | None = None) -> datetime:
        current = now or datetime.now(timezone.utc)
        return current - timedelta(days=days)

    async def count_expired(self, session: AsyncSession) -> dict[str, int]:
        return {
            "query_logs": await self._count_query_logs(session),
            "query_feedback": await self._count_feedback(session),
            "conversations_unsaved": await self._count_unsaved_conversations(session),
            "messages_unsaved": await self._count_messages_for_unsaved(session),
        }

    async def purge_expired(self, session: AsyncSession) -> dict[str, int]:
        removed_messages = await self._purge_unsaved_messages(session)
        removed_conversations = await self._purge_unsaved_conversations(session)
        removed_query_logs = await self._purge_query_logs(session)
        removed_feedback = await self._purge_feedback(session)
        await session.commit()
        return {
            "messages": removed_messages,
            "conversations": removed_conversations,
            "query_logs": removed_query_logs,
            "query_feedback": removed_feedback,
        }

    async def _purge_query_logs(self, session: AsyncSession) -> int:
        cutoff = self.cutoff(self.query_log_retention_days())
        result = await session.execute(delete(QueryLog).where(QueryLog.created_at < cutoff))
        return int(result.rowcount or 0)

    async def _purge_feedback(self, session: AsyncSession) -> int:
        cutoff = self.cutoff(self.feedback_retention_days())
        result = await session.execute(delete(QueryFeedback).where(QueryFeedback.created_at < cutoff))
        return int(result.rowcount or 0)

    async def _purge_unsaved_conversations(self, session: AsyncSession) -> int:
        cutoff = self.cutoff(self.conversation_retention_days())
        result = await session.execute(
            delete(Conversation).where(
                Conversation.is_saved.is_(False),
                Conversation.updated_at < cutoff,
            )
        )
        return int(result.rowcount or 0)

    async def _purge_unsaved_messages(self, session: AsyncSession) -> int:
        cutoff = self.cutoff(self.conversation_retention_days())
        expired_ids = select(Conversation.id).where(
            Conversation.is_saved.is_(False),
            Conversation.updated_at < cutoff,
        )
        result = await session.execute(
            delete(Message).where(Message.conversation_id.in_(expired_ids))
        )
        return int(result.rowcount or 0)

    async def _count_query_logs(self, session: AsyncSession) -> int:
        cutoff = self.cutoff(self.query_log_retention_days())
        result = await session.execute(select(QueryLog.id).where(QueryLog.created_at < cutoff))
        return len(result.scalars().all())

    async def _count_feedback(self, session: AsyncSession) -> int:
        cutoff = self.cutoff(self.feedback_retention_days())
        result = await session.execute(select(QueryFeedback.id).where(QueryFeedback.created_at < cutoff))
        return len(result.scalars().all())

    async def _count_unsaved_conversations(self, session: AsyncSession) -> int:
        cutoff = self.cutoff(self.conversation_retention_days())
        result = await session.execute(
            select(Conversation.id).where(
                Conversation.is_saved.is_(False),
                Conversation.updated_at < cutoff,
            )
        )
        return len(result.scalars().all())

    async def _count_messages_for_unsaved(self, session: AsyncSession) -> int:
        cutoff = self.cutoff(self.conversation_retention_days())
        expired_ids = select(Conversation.id).where(
            Conversation.is_saved.is_(False),
            Conversation.updated_at < cutoff,
        )
        result = await session.execute(
            select(Message.id).where(Message.conversation_id.in_(expired_ids))
        )
        return len(result.scalars().all())

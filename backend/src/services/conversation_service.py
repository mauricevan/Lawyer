"""Conversation management for multi-turn legal Q&A."""
import uuid
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.src.models.tables import Conversation, Message, QueryLog
from shared.schemas.conversation import ConversationSummary, CreateConversationRequest
from shared.schemas.query import AnswerResponse


def _serialize_answer_metadata(answer: AnswerResponse) -> dict | None:
    meta: dict = {}
    if answer.coverage_status:
        meta["coverage_status"] = answer.coverage_status
    if answer.coverage_guidance:
        meta["coverage_guidance"] = answer.coverage_guidance.model_dump(mode="json")
    if answer.verification_questions:
        meta["verification_questions"] = answer.verification_questions
    if answer.confidence_score is not None:
        meta["confidence_score"] = answer.confidence_score
    if answer.retrieval_route:
        meta["retrieval_route"] = answer.retrieval_route
    return meta or None


class ConversationService:
    """Manages conversation threads and audit trail."""

    async def create(
        self, session: AsyncSession, req: CreateConversationRequest
    ) -> Conversation:
        conv = Conversation(
            title=req.title or "Nieuw gesprek",
            query_mode=req.query_mode,
        )
        session.add(conv)
        await session.commit()
        await session.refresh(conv)
        return conv

    async def get_context(self, session: AsyncSession, conversation_id: str) -> list[dict]:
        result = await session.execute(
            select(Message)
            .where(Message.conversation_id == uuid.UUID(conversation_id))
            .order_by(Message.created_at)
        )
        messages = result.scalars().all()
        return [{"role": m.role, "content": m.content} for m in messages]

    async def append(
        self,
        session: AsyncSession,
        conversation_id: str,
        question: str,
        answer: AnswerResponse,
        chunk_ids: list[str] | None = None,
    ) -> None:
        conv_id = uuid.UUID(conversation_id)
        user_msg = Message(
            conversation_id=conv_id,
            role="user",
            content=question,
        )
        assistant_msg = Message(
            conversation_id=conv_id,
            role="assistant",
            content=answer.answer,
            citations=[c.model_dump(mode="json") for c in answer.citations],
            chunk_ids=chunk_ids,
            message_metadata=_serialize_answer_metadata(answer),
        )
        session.add(user_msg)
        session.add(assistant_msg)
        log = QueryLog(
            conversation_id=conv_id,
            question=question,
            query_mode="open",
            chunk_ids=chunk_ids,
        )
        session.add(log)
        await session.commit()

    async def get_conversation(
        self, session: AsyncSession, conversation_id: str
    ) -> Conversation | None:
        result = await session.execute(
            select(Conversation).where(Conversation.id == uuid.UUID(conversation_id))
        )
        return result.scalar_one_or_none()

    async def list_messages(self, session: AsyncSession, conversation_id: str) -> list[Message]:
        result = await session.execute(
            select(Message)
            .where(Message.conversation_id == uuid.UUID(conversation_id))
            .order_by(Message.created_at)
        )
        return list(result.scalars().all())

    async def list_saved(
        self, session: AsyncSession, saved_only: bool = True
    ) -> list[ConversationSummary]:
        query = select(Conversation)
        if saved_only:
            query = query.where(Conversation.is_saved.is_(True))
        result = await session.execute(query.order_by(Conversation.updated_at.desc()))
        convs = result.scalars().all()
        summaries = []
        for c in convs:
            msgs = await self.list_messages(session, str(c.id))
            summaries.append(ConversationSummary(
                id=str(c.id),
                title=c.title,
                query_mode=c.query_mode,
                is_saved=c.is_saved,
                created_at=c.created_at,
                updated_at=c.updated_at,
                message_count=len(msgs),
            ))
        return summaries

    async def save_conversation(
        self, session: AsyncSession, conversation_id: str, title: str | None = None
    ) -> None:
        conv = await self.get_conversation(session, conversation_id)
        if conv:
            conv.is_saved = True
            if title:
                conv.title = title
            await session.commit()

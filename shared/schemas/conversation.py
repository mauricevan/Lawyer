"""Conversation message schemas."""
from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field

from shared.schemas.citation import Citation


class MessageMetadata(BaseModel):
    """Optional assistant message metadata for coverage and retrieval."""

    coverage_status: str | None = None
    coverage_guidance: dict[str, Any] | None = None
    verification_questions: list[str] = Field(default_factory=list)
    confidence_score: float | None = None
    retrieval_route: str | None = None


class Message(BaseModel):
    """A single message in a conversation thread."""

    id: str
    role: str
    content: str
    citations: list[Citation] = Field(default_factory=list)
    metadata: MessageMetadata | None = None
    created_at: datetime


class ConversationSummary(BaseModel):
    """Summary for conversation list / dossiers."""

    id: str
    title: str
    query_mode: str = "open"
    is_saved: bool = False
    created_at: datetime
    updated_at: datetime
    message_count: int = 0


class CreateConversationRequest(BaseModel):
    """Request to start a new conversation."""

    query_mode: Literal["open", "compliance", "compare", "updates"] = "open"
    title: str | None = Field(default=None, max_length=200)


class RetrievalStatusEvent(BaseModel):
    """SSE event during query processing."""

    step: str
    message: str
    detail: dict[str, Any] | None = None

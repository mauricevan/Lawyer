"""Query and answer request/response schemas."""
from typing import Literal

from pydantic import BaseModel, Field

from shared.schemas.citation import Citation

QueryMode = Literal["open", "compliance", "compare", "updates"]
Audience = Literal["layperson", "professional"]


class QueryFilters(BaseModel):
    """Optional filters for retrieval."""

    doc_type: str | None = None
    language: str | None = None
    year: int | None = None
    in_force_only: bool = True
    consolidated_preferred: bool = True


class QueryRequest(BaseModel):
    """Incoming query from the frontend."""

    question: str = Field(..., min_length=3, max_length=2000)
    conversation_id: str | None = None
    query_mode: QueryMode = "open"
    audience: Audience = "layperson"
    filters: QueryFilters | None = None
    language: str = "nl"


class AnswerResponse(BaseModel):
    """Structured answer with citations."""

    answer: str
    conversation_id: str
    citations: list[Citation] = Field(default_factory=list)
    disclaimer: str = "Dit is geen juridisch advies."

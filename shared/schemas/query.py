"""Query and answer request/response schemas."""
from typing import Literal

from pydantic import BaseModel, Field

from shared.schemas.citation import Citation
from shared.schemas.coverage_guidance import CoverageGuidance, CoverageStatus
from shared.schemas.legal_hypothesis import LegalHypothesis
from shared.schemas.retrieval_explainability import RetrievalExplainability
from shared.schemas.validation_patterns import (
    CELEX_PATTERN,
    FILTER_TEXT_PATTERN,
    LANGUAGE_PATTERN,
    UUID_PATTERN,
)

QueryMode = Literal["open", "compliance", "compare", "updates"]
Audience = Literal["layperson", "professional"]
RetrievalRoute = Literal[
    "local", "live_fallback", "hybrid", "cache", "layperson_topic", "cn_classification",
    "agent_flow", "declarant_flow",
]


class QueryFilters(BaseModel):
    """Optional filters for retrieval."""

    domain: str | None = Field(default=None, max_length=64, pattern=FILTER_TEXT_PATTERN)
    doc_type: str | None = Field(default=None, max_length=64, pattern=FILTER_TEXT_PATTERN)
    celex: str | None = Field(default=None, max_length=32, pattern=CELEX_PATTERN)
    language: str | None = Field(default=None, max_length=8, pattern=LANGUAGE_PATTERN)
    year: int | None = Field(default=None, ge=1950, le=2100)
    time_context: Literal["current", "historical"] | None = None
    in_force_only: bool = True
    include_deprecated: bool = False
    consolidated_preferred: bool = True
    intent_id: str | None = Field(default=None, max_length=64)
    router_confidence: float | None = Field(default=None, ge=0.0, le=1.0)
    domain_cluster: str | None = Field(default=None, max_length=64)


class QueryRequest(BaseModel):
    """Incoming query from the frontend."""

    question: str = Field(..., min_length=3, max_length=2000)
    conversation_id: str | None = Field(default=None, pattern=UUID_PATTERN)
    query_mode: QueryMode = "open"
    audience: Audience = "layperson"
    filters: QueryFilters | None = None
    language: str = Field(default="nl", min_length=2, max_length=8, pattern=LANGUAGE_PATTERN)


class AnswerResponse(BaseModel):
    """Structured answer with citations."""

    answer: str
    conversation_id: str
    citations: list[Citation] = Field(default_factory=list)
    disclaimer: str = "Dit is geen juridisch advies."
    retrieval_route: RetrievalRoute | None = None
    confidence_score: float | None = None
    verification_questions: list[str] = Field(default_factory=list)
    retrieval_explainability: RetrievalExplainability | None = None
    coverage_guidance: CoverageGuidance | None = None
    coverage_status: CoverageStatus | None = None
    clarification_prompt: str | None = None
    legal_hypothesis: LegalHypothesis | None = None

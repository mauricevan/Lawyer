"""Retrieval explainability schemas for API responses (plan12 AB)."""
from typing import Literal

from pydantic import BaseModel, Field

RetrievalRoute = Literal["local", "live_fallback", "hybrid", "cache"]


class RouterDecision(BaseModel):
    """Router output exposed for transparency."""

    domains: list[str] = Field(default_factory=list)
    doc_types: list[str] = Field(default_factory=list)
    celex_hint: str | None = None
    language: str = "nl"
    time_context: str | None = None
    intent_id: str | None = None
    confidence: float | None = None
    domain_cluster: str | None = None


class SourceScoreBreakdown(BaseModel):
    """Per-chunk retrieval score metadata."""

    chunk_id: str
    celex: str
    vector_score: float | None = None
    rerank_score: float | None = None


class RetrievalExplainability(BaseModel):
    """Structured retrieval rationale for clients."""

    route: RetrievalRoute
    query_language: str
    router: RouterDecision
    reranker_variant: str
    rerank_latency_ms: float
    hybrid_rrf_enabled: bool
    stage_counts: dict[str, int] = Field(default_factory=dict)
    sources: list[SourceScoreBreakdown] = Field(default_factory=list)

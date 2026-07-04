"""Legal interpretation plan schemas for EUR-Lex Reading Agent (ADR-0009 fase 2)."""
from typing import Literal

from pydantic import BaseModel, Field

from shared.schemas.validation_patterns import CELEX_PATTERN

QuestionType = Literal["obligation", "definition", "procedure", "comparison", "scope", "other"]
FetchSource = Literal["cache", "live", "mixed"]


class InstrumentTarget(BaseModel):
    """EU legal instrument identified from the question."""

    celex: str | None = Field(default=None, max_length=32, pattern=CELEX_PATTERN)
    oj_citation: str | None = Field(default=None, max_length=32)
    name: str = Field(..., min_length=1, max_length=256)
    articles: list[str] = Field(default_factory=list)
    confidence: float = Field(default=0.5, ge=0.0, le=1.0)
    title: str | None = Field(default=None, max_length=512)


class LegalInterpretationPlan(BaseModel):
    """Structured output from LLM or rule-based legal planner."""

    question_type: QuestionType = "other"
    is_eu_law: bool = True
    is_national_law: bool = False
    instruments: list[InstrumentTarget] = Field(default_factory=list)
    search_keywords: list[str] = Field(default_factory=list)
    confidence: float = Field(default=0.5, ge=0.0, le=1.0)
    reasoning_brief: str = Field(default="", max_length=200)
    planner_source: Literal["llm", "rule_fallback"] = "llm"


class AgentFetchResult(BaseModel):
    """Result of article fetch orchestration."""

    chunks: list[dict] = Field(default_factory=list)
    route: str = "agent_flow"
    fetch_source: FetchSource = "live"
    fetch_ok: bool = False
    articles_fetched: list[str] = Field(default_factory=list)
    resolved_celex: list[str] = Field(default_factory=list)
    attempted_celex: list[str] = Field(default_factory=list)
    fetch_attempted: bool = False

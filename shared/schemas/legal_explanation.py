"""Immutable explanation engine contracts — single source of truth after compose."""
from datetime import datetime
from enum import Enum
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from shared.schemas.citation import Citation
from shared.schemas.coverage_guidance import CoverageStatus

PUBLISH_GUARD_VERSION = "2026.07.05.1"


class ExplanationSectionKey(str, Enum):
    short_answer = "short_answer"
    law_says = "law_says"
    practical_meaning = "practical_meaning"
    legal_sources = "legal_sources"
    uncertainties = "uncertainties"
    disclaimer = "disclaimer"


class ClaimGrounding(str, Enum):
    source = "source"
    interpretation = "interpretation"
    gap = "gap"


class ExplanationClaim(BaseModel):
    model_config = ConfigDict(frozen=True)

    claim_id: str
    text: str
    grounding: ClaimGrounding
    citation_ids: tuple[str, ...] = ()


class ExplanationSections(BaseModel):
    model_config = ConfigDict(frozen=True)

    short_answer: str
    law_says: str
    practical_meaning: str
    legal_sources: str
    uncertainties: str
    disclaimer: str


class LegalExplanationDraft(BaseModel):
    model_config = ConfigDict(frozen=True)

    sections: ExplanationSections
    claims: tuple[ExplanationClaim, ...] = ()
    citations: tuple[Citation, ...] = ()
    coverage_status: CoverageStatus
    retrieval_context_id: str
    quality: dict = Field(default_factory=dict)
    coverage_guidance: dict | None = None


class PublishedExplanation(BaseModel):
    model_config = ConfigDict(frozen=True)

    draft: LegalExplanationDraft
    published_at: datetime
    publish_guard_version: str = PUBLISH_GUARD_VERSION


class GapReason(str, Enum):
    retrieval_failure = "retrieval_failure"
    citation_failure = "citation_failure"
    validation_failure = "validation_failure"


class SafePartialKnowledge(BaseModel):
    model_config = ConfigDict(frozen=True)

    instruments_consulted: tuple[str, ...] = ()
    topics_identified: tuple[str, ...] = ()
    factual_gaps: tuple[str, ...] = ()


class GapResponse(BaseModel):
    model_config = ConfigDict(frozen=True)

    reason: GapReason
    sections: ExplanationSections
    safe_partial: SafePartialKnowledge | None = None
    coverage_status: Literal["insufficient"] = "insufficient"
    quality: dict = Field(default_factory=dict)
    coverage_guidance: dict | None = None
    citations: tuple[Citation, ...] = ()


class InternalAnalysisTrace(BaseModel):
    """Read-only analytics — never merged into user answer."""
    model_config = ConfigDict(frozen=True)

    trace_id: str
    source_context_id: str
    legal_judge: dict | None = None
    case_law_simulation: dict | None = None
    multi_judge_panel: dict | None = None


class ExplanationEngineResult(BaseModel):
    """Pipeline output — either published explanation or gap."""
    model_config = ConfigDict(frozen=True)

    answer_markdown: str
    published: PublishedExplanation | None = None
    gap: GapResponse | None = None
    citations: tuple[Citation, ...] = ()
    disclaimer: str = ""
    coverage_status: CoverageStatus
    quality: dict = Field(default_factory=dict)
    coverage_guidance: dict | None = None
    retrieval_context_id: str = ""

"""Schemas for coverage-gap guidance when corpus is insufficient."""
from typing import Literal

from pydantic import BaseModel, Field

CoverageStatus = Literal["adequate", "insufficient", "irrelevant", "clarify_only"]
CoverageReason = Literal[
    "no_chunks",
    "low_confidence",
    "irrelevant_retrieval",
    "topic_not_in_corpus",
    "fetch_attempted",
    "insufficient_evidence",
]
ReferralType = Literal["authority", "legal_aid", "union"]


class CoverageFramework(BaseModel):
    name: str
    summary: str


class CoverageReferral(BaseModel):
    label: str
    url: str
    type: ReferralType


class CoverageGuidance(BaseModel):
    topic_id: str
    sensitivity: Literal["low", "high"] = "low"
    empathy_opener: str = ""
    frameworks: list[CoverageFramework] = Field(default_factory=list)
    referrals: list[CoverageReferral] = Field(default_factory=list)


class AdequacyResult(BaseModel):
    is_adequate: bool
    reason: CoverageReason | None = None
    coverage_status: CoverageStatus = "adequate"

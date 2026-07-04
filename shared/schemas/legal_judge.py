"""V7 adversarial legal judge output schema."""
from typing import Literal

from pydantic import BaseModel, Field

JudgePassFail = Literal["pass", "fail"]
JudgeSeverity = Literal["low", "medium", "high"]
JudgeRecommendation = Literal["approve", "revise", "regenerate"]

JudgeIssueCode = Literal[
    "wrong_legal_basis",
    "missing_legal_basis",
    "domain_inconsistency",
    "wrong_legal_effect",
    "overconfident_conclusion",
    "missing_exception_analysis",
    "reasoning_jump",
    "missing_effect_section",
]


class LegalJudgeResult(BaseModel):
    """Outcome of adversarial review before user-facing output."""

    pass_fail: JudgePassFail
    issues_found: list[JudgeIssueCode] = Field(default_factory=list, max_length=10)
    severity: JudgeSeverity = "low"
    recommendation: JudgeRecommendation = "approve"
    rationale: str = Field(default="", max_length=400)

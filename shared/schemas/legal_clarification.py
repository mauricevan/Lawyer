"""V10.3 Interactive Legal Clarification Layer (ILCL) schemas."""
from typing import Literal

from pydantic import BaseModel, Field

ClarificationState = Literal["clear", "ambiguous", "unanswerable"]
ClarificationMode = Literal["questions", "scenarios", "assumption", "skip"]


class ClarificationQuestion(BaseModel):
    """Single clarification prompt for the user."""

    id: str = Field(..., max_length=40)
    prompt: str = Field(..., max_length=300)
    options: list[str] = Field(default_factory=list, max_length=6)


class ClarificationScenario(BaseModel):
    """Suggested legal interpretation path."""

    id: str = Field(..., max_length=8)
    label: str = Field(..., max_length=120)
    description: str = Field(..., max_length=300)
    frameworks: list[str] = Field(default_factory=list, max_length=4)


class LegalClarificationResult(BaseModel):
    """V10.3 ILCL output — pre-retrieval clarification decision."""

    state: ClarificationState
    mode: ClarificationMode = "skip"
    ambiguity_score: float = Field(default=0.0, ge=0.0, le=1.0)
    ambiguity_reasons: list[str] = Field(default_factory=list, max_length=6)
    questions: list[ClarificationQuestion] = Field(default_factory=list, max_length=4)
    scenarios: list[ClarificationScenario] = Field(default_factory=list, max_length=4)
    assumption_text: str = Field(default="", max_length=400)
    enriched_question: str = Field(default="", max_length=2500)
    formatted_section: str = Field(default="", max_length=4000)
    should_proceed: bool = True

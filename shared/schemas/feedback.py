"""Feedback schemas for pilot quality capture."""
from typing import Literal

from pydantic import BaseModel, Field

from shared.schemas.validation_patterns import UUID_PATTERN

FeedbackCategory = Literal["incorrect", "incomplete", "source_issue", "ux", "positive"]

CATEGORY_LABELS_NL: dict[FeedbackCategory, str] = {
    "incorrect": "Onjuist",
    "incomplete": "Onvolledig",
    "source_issue": "Bronprobleem",
    "ux": "Gebruiksvriendelijkheid",
    "positive": "Positief",
}


class FeedbackRequest(BaseModel):
    rating: int = Field(..., ge=1, le=5)
    category: FeedbackCategory | None = None
    comment: str | None = Field(default=None, max_length=1000)
    conversation_id: str | None = Field(default=None, pattern=UUID_PATTERN)

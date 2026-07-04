"""Evidence validation result — pre-answer legal grounding check."""
from typing import Literal

from pydantic import BaseModel, Field

EvidenceFailureReason = Literal[
    "no_chunks",
    "procedural_only",
    "domain_mismatch",
    "actor_mismatch",
    "subject_mismatch",
    "insufficient_substance",
    "effect_mismatch",
]


class EvidenceValidationResult(BaseModel):
    """Outcome of validating retrieved EUR-Lex chunks against the question."""

    is_valid: bool = False
    reasons: list[EvidenceFailureReason] = Field(default_factory=list)
    validated_chunks: list[dict] = Field(default_factory=list)
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)

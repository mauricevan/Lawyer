"""V5.1 conflict-aware CELEX resolution output."""
from typing import Literal

from pydantic import BaseModel, Field

from shared.schemas.legal_interpretation import InstrumentTarget, LegalRoutingDomain

CelexRejectionReason = Literal[
    "planner_domain_mismatch",
    "conflict_domain_mismatch",
    "forbidden_for_conflict",
    "low_confidence_score",
    "none",
]


class CelexResolutionResult(BaseModel):
    """Outcome of conflict-aware CELEX selection."""

    final_domain: LegalRoutingDomain
    final_celex: list[str] = Field(default_factory=list, max_length=5)
    rejected_celex: list[str] = Field(default_factory=list, max_length=10)
    rejection_reason: CelexRejectionReason = "none"
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    instruments: list[InstrumentTarget] = Field(default_factory=list, max_length=5)
    needs_domain_retrieval: bool = False

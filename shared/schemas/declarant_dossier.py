"""Declarant pipeline dossier — think → clarify → fetch → verify → answer."""
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field

from shared.schemas.legal_clarification import LegalClarificationResult
from shared.schemas.legal_conflict import LegalCaseAnalysis


class DeclarantPhase(str, Enum):
    """Pipeline phase for telemetry and tests."""

    THINK = "think"
    CLARIFY = "clarify"
    FETCH = "fetch"
    VERIFY = "verify"
    ANSWER = "answer"
    GAP = "gap"


class DeclarantThinkResult(BaseModel):
    """Output of the think step — no EUR-Lex calls."""

    phase: DeclarantPhase
    ready_to_search: bool
    effective_question: str
    user_goal: str = ""
    analysis: LegalCaseAnalysis | None = None
    hypothesis_celex: tuple[str, ...] = ()
    articles_by_celex: dict[str, tuple[str, ...]] = Field(default_factory=dict)
    ilcl_result: LegalClarificationResult | None = None
    gap_reason: str | None = None


class DeclarantDossier(BaseModel):
    """Accumulated state for one declarant pipeline run."""

    original_question: str
    effective_question: str = ""
    clarification_rounds: int = 0
    phase: DeclarantPhase = DeclarantPhase.THINK
    think: DeclarantThinkResult | None = None
    fetched_chunks: list[dict[str, Any]] = Field(default_factory=list)
    verification_ok: bool = False

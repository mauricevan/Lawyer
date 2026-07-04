"""Legal hypothesis — step 1 reasoning before any EUR-Lex retrieval (v3/v4)."""
from typing import Literal

from pydantic import BaseModel, Field

from shared.schemas.legal_conflict import PrimaryLegalConflict, ReconciliationConclusion
from shared.schemas.legal_interpretation import LegalActor, LegalQuestionType, LegalRoutingDomain

HypothesisSource = Literal["llm", "rule"]


class LegalHypothesis(BaseModel):
    """Structured legal problem analysis without source documents."""

    legal_problem: str = Field(..., min_length=8, max_length=500)
    legal_actor: LegalActor = "unknown"
    legal_domain_guess: LegalRoutingDomain = "unknown"
    likely_eu_frameworks: list[str] = Field(default_factory=list, max_length=8)
    legal_question_type: LegalQuestionType = "unknown"
    source: HypothesisSource = "rule"
    case_summary: str | None = None
    parties: list[str] = Field(default_factory=list, max_length=6)
    context: str = ""
    possible_domains: list[str] = Field(default_factory=list, max_length=4)
    primary_legal_conflict: PrimaryLegalConflict | None = None
    reconciliation_conclusion: ReconciliationConclusion | None = None

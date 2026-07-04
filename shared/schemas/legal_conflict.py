"""V4 primary legal conflict and reconciliation schemas."""
from typing import Literal

from pydantic import BaseModel, Field

from shared.schemas.legal_effect import LegalEffectAnalysis
from shared.schemas.legal_interpretation import LegalActor, LegalQuestionType, LegalRoutingDomain

PrimaryLegalConflict = Literal[
    "internal_market_restriction",
    "consumer_transaction_issue",
    "employment_relationship_issue",
    "data_processing_issue",
    "product_compliance_issue",
    "administrative_enforcement_issue",
    "platform_governance_issue",
]

ReconciliationConclusion = Literal["supported", "partially_supported", "contradicted"]


class LegalCaseAnalysis(BaseModel):
    """V4 case analysis: hypothesis + single primary conflict + mapped domain."""

    case_summary: str = Field(..., min_length=8, max_length=500)
    parties: list[str] = Field(default_factory=list, max_length=6)
    context: str = Field(default="", max_length=200)
    possible_domains: list[LegalRoutingDomain] = Field(default_factory=list, max_length=4)
    primary_legal_conflict: PrimaryLegalConflict
    legal_domain: LegalRoutingDomain
    legal_actor: LegalActor = "unknown"
    legal_question_type: LegalQuestionType = "unknown"
    likely_eu_frameworks: list[str] = Field(default_factory=list, max_length=8)
    default_celex: str | None = None
    legal_effect: LegalEffectAnalysis | None = None


class ReconciliationResult(BaseModel):
    """Outcome of comparing case analysis with validated EUR-Lex evidence."""

    conclusion: ReconciliationConclusion
    rationale: str = Field(default="", max_length=300)

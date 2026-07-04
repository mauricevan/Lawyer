"""V8.1 structured case law simulation (CJEU arrest format)."""
from typing import Literal

from pydantic import BaseModel, Field

CourtSimulationResult = Literal[
    "compatible_with_eu_law",
    "incompatible_with_eu_law",
    "compatible_under_conditions",
]

AlignmentWithAnswer = Literal["consistent", "partially_consistent", "inconsistent"]

CourtFinalConclusion = Literal["permitted", "permitted_under_conditions", "prohibited"]

LegalEffectClassification = Literal[
    "prohibited restriction",
    "justified and proportionate restriction",
    "justified but disproportionate restriction",
    "no restriction under EU law",
]

StructureEnforcement = Literal["pass", "fail", "regenerate"]


class ProportionalitySteps(BaseModel):
    """Mandatory three-step proportionality sub-engine."""

    suitability: str = Field(..., min_length=8, max_length=400)
    necessity: str = Field(..., min_length=8, max_length=400)
    balancing: str = Field(..., min_length=8, max_length=400)
    is_complete: bool = True


class StructuredJudgment(BaseModel):
    """Fixed seven-section CJEU-style judgment — no deviations allowed."""

    issue: str = Field(..., min_length=20, max_length=500)
    applicable_eu_law: list[str] = Field(..., min_length=1, max_length=6)
    restriction_analysis: str = Field(..., min_length=20, max_length=500)
    legitimate_aim: str = Field(..., min_length=8, max_length=300)
    proportionality: ProportionalitySteps
    court_conclusion: str = Field(..., min_length=20, max_length=500)
    legal_effect_classification: LegalEffectClassification


class CaseLawSimulationResult(BaseModel):
    """Judicial reality check after adversarial judge."""

    hypothetical_case_title: str = Field(default="Commission v Member State X (hypothetical)", max_length=200)
    issue_statement: str = Field(default="", max_length=500)
    has_eu_restriction: bool = False
    restriction_types: list[str] = Field(default_factory=list, max_length=4)
    possible_justifications: list[str] = Field(default_factory=list, max_length=5)
    proportionality_assessment: str = Field(default="", max_length=200)
    court_final_conclusion: CourtFinalConclusion = "permitted_under_conditions"
    court_simulation_result: CourtSimulationResult = "compatible_under_conditions"
    reasoning_summary: str = Field(default="", max_length=400)
    alignment_with_answer: AlignmentWithAnswer = "partially_consistent"
    structured_judgment: StructuredJudgment | None = None
    formatted_judgment: str = Field(default="", max_length=4000)
    structure_valid: bool = False
    structure_enforcement: StructureEnforcement = "pass"

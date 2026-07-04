"""V6 legal effect classification — what EU law does to the national measure."""
from typing import Literal

from pydantic import BaseModel, Field

LegalEffectType = Literal[
    "market_access_prohibition",
    "discrimination_by_establishment",
    "additional_requirement",
    "licensing_or_authorisation",
    "procedural_burden",
    "enforcement_measure",
]

RestrictionStrength = Literal["high", "medium", "low"]

StateActionType = Literal[
    "ban",
    "requirement",
    "licensing",
    "discrimination",
    "enforcement",
    "transparency",
    "eligibility_requirement",
]

EffectConclusionHint = Literal["permitted", "prohibited", "conditional"]


class LegalEffectAnalysis(BaseModel):
    """Juridical effect of the state measure — drives law selection and answer framing."""

    legal_effect_type: LegalEffectType
    restriction_strength: RestrictionStrength = "medium"
    state_action: StateActionType = "requirement"
    effect_conclusion_hint: EffectConclusionHint = "conditional"

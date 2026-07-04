"""V8.1 proportionality engine — suitability, necessity, balancing."""
from dataclasses import dataclass

from shared.schemas.legal_conflict import LegalCaseAnalysis
from shared.schemas.legal_effect import LegalEffectType

_HIGH_RESTRICTION_EFFECTS = frozenset({
    "discrimination_by_establishment",
    "market_access_prohibition",
})


@dataclass(frozen=True)
class ProportionalityAssessment:
    """Full three-step proportionality outcome with arrest-style text."""

    is_suitable: bool
    is_necessary: bool
    passes_balancing: bool
    suitability_text: str
    necessity_text: str
    balancing_text: str
    summary: str
    passes_overall: bool

    @property
    def is_complete(self) -> bool:
        return bool(self.suitability_text and self.necessity_text and self.balancing_text)


def assess_proportionality(analysis: LegalCaseAnalysis) -> ProportionalityAssessment:
    """Apply CJEU-style proportionality test to the national measure."""
    effect = analysis.legal_effect
    if not effect:
        return _neutral_assessment()
    if effect.legal_effect_type in _HIGH_RESTRICTION_EFFECTS and effect.restriction_strength == "high":
        return _strict_services_restriction(analysis)
    if effect.legal_effect_type == "additional_requirement":
        return _fails_necessity(
            "The measure may contribute to consumer protection.",
            "Less restrictive means exist (transparency obligations, targeted enforcement).",
            "The burden on cross-border services outweighs the demonstrated benefit.",
        )
    if effect.legal_effect_type == "licensing_or_authorisation":
        return _fails_necessity(
            "The measure may contribute to consumer protection and online safety.",
            "Less restrictive means exist (post-hoc enforcement, transparency obligations).",
            "The burden on market access outweighs the benefit.",
        )
    if effect.legal_effect_type == "enforcement_measure":
        return _passes_all(
            "The measure contributes to effective market surveillance.",
            "No equally effective less restrictive alternative is apparent.",
            "The burden on operators is proportionate to enforcement needs.",
        )
    return _fails_necessity(
        "The measure may contribute to the stated public-interest objective.",
        "Less restrictive means exist (targeted rules, post-hoc enforcement).",
        "The restriction on EU freedoms outweighs the national benefit.",
    )


def _neutral_assessment() -> ProportionalityAssessment:
    return ProportionalityAssessment(
        is_suitable=True,
        is_necessary=True,
        passes_balancing=True,
        suitability_text="No classified restriction requiring proportionality review.",
        necessity_text="No less restrictive alternative assessment required.",
        balancing_text="No balancing exercise required.",
        summary="no effect classified",
        passes_overall=True,
    )


def _passes_all(suit: str, nec: str, bal: str) -> ProportionalityAssessment:
    return ProportionalityAssessment(True, True, True, suit, nec, bal, "passes proportionality", True)


def _fails_necessity(suit: str, nec: str, bal: str) -> ProportionalityAssessment:
    return ProportionalityAssessment(
        is_suitable=True,
        is_necessary=False,
        passes_balancing=False,
        suitability_text=suit,
        necessity_text=nec,
        balancing_text=bal,
        summary="fails necessity test",
        passes_overall=False,
    )


def _strict_services_restriction(analysis: LegalCaseAnalysis) -> ProportionalityAssessment:
    context = analysis.context.lower()
    summary_text = analysis.case_summary.lower()
    is_broad = any(
        hint in context or hint in summary_text
        for hint in ("e-commerce", "platform", "adverteerder", "eu gevestigd", "eu-only")
    )
    if is_broad:
        return _fails_necessity(
            "The measure may contribute to consumer protection.",
            "Less restrictive means exist (targeted transparency, post-hoc enforcement, fraud filters).",
            "The blanket establishment criterion disproportionately restricts cross-border services.",
        )
    return _fails_necessity(
        "The measure may contribute to the stated objective.",
        "Less restrictive means exist (narrower eligibility rules, case-by-case review).",
        "The burden on market access outweighs the benefit.",
    )

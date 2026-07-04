"""V6 — classify juridical effect of a national measure before retrieval."""
from shared.schemas.legal_conflict import LegalCaseAnalysis, PrimaryLegalConflict
from shared.schemas.legal_effect import (
    EffectConclusionHint,
    LegalEffectAnalysis,
    LegalEffectType,
    RestrictionStrength,
    StateActionType,
)

_ESTABLISHMENT_HINTS = (
    "eu gevestigd", "in de eu gevestigd", "vestiging", "establishment",
    "niet-eu", "buiten de eu", "alleen toe te laten", "eligibility",
)
_LICENSING_HINTS = ("vergunning", "toestemming", "authorisation", "authorization", "licentie")
_ENFORCEMENT_HINTS = ("handhaving", "toezicht", "sanctie", "markttoezicht")
_PROCEDURAL_HINTS = ("administratief", "registratie", "meldingsplicht", "documentatieplicht")
_MARKET_BAN_HINTS = ("verbod", "uitsluiten van de markt", "markttoegang", "toegang tot de markt")
_EXTRA_REQUIREMENT_HINTS = ("extra eis", "aanvullende eis", "bovenop", "extra voorwaarde", "verplicht")


class LegalEffectService:
    """Determine what the national measure does juridically — not which law applies."""

    def classify(self, question: str, analysis: LegalCaseAnalysis) -> LegalEffectAnalysis:
        """Rule-based effect classification from question + conflict context."""
        lowered = question.lower()
        effect_type = self._effect_type(lowered, analysis.primary_legal_conflict)
        state_action = self._state_action(lowered, effect_type)
        strength = self._restriction_strength(lowered, effect_type)
        conclusion = self._conclusion_hint(effect_type, strength, analysis.primary_legal_conflict)
        return LegalEffectAnalysis(
            legal_effect_type=effect_type,
            restriction_strength=strength,
            state_action=state_action,
            effect_conclusion_hint=conclusion,
        )

    def _effect_type(self, lowered: str, conflict: PrimaryLegalConflict) -> LegalEffectType:
        if _matches(lowered, _ENFORCEMENT_HINTS) and conflict == "administrative_enforcement_issue":
            return "enforcement_measure"
        if _matches(lowered, _ESTABLISHMENT_HINTS):
            return "discrimination_by_establishment"
        if _matches(lowered, _LICENSING_HINTS):
            return "licensing_or_authorisation"
        if _matches(lowered, _MARKET_BAN_HINTS):
            return "market_access_prohibition"
        if _matches(lowered, _PROCEDURAL_HINTS):
            return "procedural_burden"
        if _matches(lowered, _EXTRA_REQUIREMENT_HINTS) or conflict == "internal_market_restriction":
            return "additional_requirement"
        return _fallback_effect(conflict)

    def _state_action(self, lowered: str, effect_type: LegalEffectType) -> StateActionType:
        if effect_type == "discrimination_by_establishment":
            return "eligibility_requirement"
        if effect_type == "licensing_or_authorisation":
            return "licensing"
        if effect_type == "enforcement_measure":
            return "enforcement"
        if effect_type == "market_access_prohibition":
            return "ban"
        if "transparant" in lowered:
            return "transparency"
        if "verplicht" in lowered or "eis" in lowered:
            return "requirement"
        return "requirement"

    def _restriction_strength(self, lowered: str, effect_type: LegalEffectType) -> RestrictionStrength:
        if effect_type in {"market_access_prohibition", "discrimination_by_establishment"}:
            if any(h in lowered for h in ("alleen", "uitsluitend", "verboden", "mag niet")):
                return "high"
        if effect_type == "procedural_burden":
            return "low"
        if "verplicht" in lowered:
            return "medium"
        return "medium"

    def _conclusion_hint(
        self,
        effect_type: LegalEffectType,
        strength: RestrictionStrength,
        conflict: PrimaryLegalConflict,
    ) -> EffectConclusionHint:
        if effect_type == "discrimination_by_establishment" and strength == "high":
            return "prohibited"
        if effect_type == "market_access_prohibition":
            return "prohibited"
        if effect_type == "procedural_burden":
            return "conditional"
        if conflict == "internal_market_restriction" and effect_type == "additional_requirement":
            return "conditional"
        return "conditional"


def _matches(lowered: str, hints: tuple[str, ...]) -> bool:
    return any(h in lowered for h in hints)


def _fallback_effect(conflict: PrimaryLegalConflict) -> LegalEffectType:
    mapping: dict[PrimaryLegalConflict, LegalEffectType] = {
        "internal_market_restriction": "additional_requirement",
        "consumer_transaction_issue": "additional_requirement",
        "employment_relationship_issue": "discrimination_by_establishment",
        "data_processing_issue": "procedural_burden",
        "product_compliance_issue": "additional_requirement",
        "administrative_enforcement_issue": "enforcement_measure",
        "platform_governance_issue": "procedural_burden",
    }
    return mapping.get(conflict, "additional_requirement")

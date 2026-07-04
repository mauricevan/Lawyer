"""V6 effect → law mapping; effect determines CELEX, not the reverse."""
from dataclasses import dataclass

from shared.schemas.legal_conflict import LegalCaseAnalysis, PrimaryLegalConflict
from shared.schemas.legal_effect import LegalEffectAnalysis, LegalEffectType

_TFEU_FRAMEWORK = "TFEU free movement of services and goods"


@dataclass(frozen=True)
class EffectLawMapping:
    """CELEX and frameworks driven by juridical effect type."""

    primary_celex: str
    frameworks: tuple[str, ...]
    secondary_celex: tuple[str, ...] = ()


_EFFECT_LAW_MAP: dict[LegalEffectType, EffectLawMapping] = {
    "discrimination_by_establishment": EffectLawMapping(
        primary_celex="32000L0031",
        frameworks=(
            _TFEU_FRAMEWORK,
            "Directive 2000/31/EC country of origin information society services",
            "restriction on information society services",
        ),
    ),
    "market_access_prohibition": EffectLawMapping(
        primary_celex="32000L0031",
        frameworks=(_TFEU_FRAMEWORK, "internal market access prohibition"),
        secondary_celex=("32008R0768",),
    ),
    "additional_requirement": EffectLawMapping(
        primary_celex="32000L0031",
        frameworks=(
            "harmonisation directive additional national requirements",
            "Directive 2000/31/EC coordinated field",
        ),
        secondary_celex=("32008R0768",),
    ),
    "licensing_or_authorisation": EffectLawMapping(
        primary_celex="32000L0031",
        frameworks=("prior authorisation information society services", _TFEU_FRAMEWORK),
    ),
    "procedural_burden": EffectLawMapping(
        primary_celex="32000L0031",
        frameworks=("administrative obligations information society services",),
    ),
    "enforcement_measure": EffectLawMapping(
        primary_celex="32019R1020",
        frameworks=("Regulation (EU) 2019/1020 market surveillance",),
    ),
}

_CONFLICT_EFFECT_OVERRIDES: dict[tuple[PrimaryLegalConflict, LegalEffectType], EffectLawMapping] = {
    ("employment_relationship_issue", "discrimination_by_establishment"): EffectLawMapping(
        primary_celex="32000L0078",
        frameworks=("Directive 2000/78/EC equal treatment employment",),
    ),
    ("data_processing_issue", "procedural_burden"): EffectLawMapping(
        primary_celex="32016R0679",
        frameworks=("Regulation (EU) 2016/679 GDPR lawful processing",),
    ),
    ("platform_governance_issue", "procedural_burden"): EffectLawMapping(
        primary_celex="32022R2065",
        frameworks=("Regulation (EU) 2022/2065 Digital Services Act",),
    ),
    ("consumer_transaction_issue", "additional_requirement"): EffectLawMapping(
        primary_celex="32011L0083",
        frameworks=("Directive 2011/83/EU consumer rights",),
    ),
}


def map_effect_to_law(
    effect: LegalEffectAnalysis,
    conflict: PrimaryLegalConflict,
) -> EffectLawMapping:
    """Return law mapping for effect; conflict-specific overrides when defined."""
    override = _CONFLICT_EFFECT_OVERRIDES.get((conflict, effect.legal_effect_type))
    if override:
        return override
    return _EFFECT_LAW_MAP[effect.legal_effect_type]


def apply_effect_to_case_analysis(analysis: LegalCaseAnalysis) -> LegalCaseAnalysis:
    """Override CELEX/frameworks from legal effect — V6 overrule principle."""
    if not analysis.legal_effect:
        return analysis
    mapping = map_effect_to_law(analysis.legal_effect, analysis.primary_legal_conflict)
    frameworks = list(dict.fromkeys([*mapping.frameworks, *analysis.likely_eu_frameworks]))
    return analysis.model_copy(update={
        "default_celex": mapping.primary_celex,
        "likely_eu_frameworks": frameworks[:8],
        "legal_effect": analysis.legal_effect,
    })


def effect_celex_candidates(effect: LegalEffectAnalysis, conflict: PrimaryLegalConflict) -> list[str]:
    """CELEX pool from effect mapping for V5.1 resolver."""
    mapping = map_effect_to_law(effect, conflict)
    return list(dict.fromkeys([mapping.primary_celex, *mapping.secondary_celex]))

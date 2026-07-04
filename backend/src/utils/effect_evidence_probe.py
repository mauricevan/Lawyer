"""V6 evidence probes — validate chunks support the juridical effect mechanism."""
from backend.src.utils.legal_chunk_text import score_chunk_relevance
from shared.schemas.legal_effect import LegalEffectAnalysis, LegalEffectType

_MIN_EFFECT_SCORE = 2

_EFFECT_PROBE_TERMS: dict[LegalEffectType, tuple[str, ...]] = {
    "discrimination_by_establishment": (
        "country of origin", "information society", "restrict", "derogation",
        "coordinated field", "diensten", "services", "vestiging",
    ),
    "market_access_prohibition": (
        "market access", "prohibition", "restrict", "internal market", "free movement",
    ),
    "additional_requirement": (
        "additional", "national", "requirement", "harmonis", "coordinated field", "derogation",
    ),
    "licensing_or_authorisation": (
        "authorisation", "authorization", "prior approval", "licence", "license",
    ),
    "procedural_burden": (
        "obligation", "procedure", "administrative", "notify", "information",
    ),
    "enforcement_measure": (
        "surveillance", "enforcement", "market surveillance", "compliance", "sanction",
    ),
}


def build_effect_evidence_probe(effect: LegalEffectAnalysis) -> str:
    """Compose validation probe from effect type and state action."""
    terms = _EFFECT_PROBE_TERMS.get(effect.legal_effect_type, ())
    return " ".join([effect.legal_effect_type.replace("_", " "), effect.state_action, *terms])


def chunk_supports_legal_effect(text: str, effect: LegalEffectAnalysis) -> bool:
    """Return True when chunk text supports the effect mechanism, not just the topic."""
    probe = build_effect_evidence_probe(effect)
    if score_chunk_relevance(text, probe) >= _MIN_EFFECT_SCORE:
        return True
    lowered = text.lower()
    terms = _EFFECT_PROBE_TERMS.get(effect.legal_effect_type, ())
    return sum(1 for term in terms if term in lowered) >= 2

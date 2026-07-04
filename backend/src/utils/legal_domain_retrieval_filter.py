"""Filter instruments and chunks by routing legal_domain — hard exclusions (V3)."""
from typing import Any

from backend.src.utils.legal_domain_inference import LegalRoutingDomain
from shared.schemas.legal_interpretation import InstrumentTarget

_GPSR_CELEX = frozenset({"32023R0988"})
_SURVEILLANCE_CELEX = frozenset({"32019R1020"})
_CUSTOMS_CELEX = frozenset({"32013R0952", "32015R2446"})
_FINANCIAL_CELEX = frozenset({"32014R0596"})
_DSA_CELEX = frozenset({"32022R2065"})
_EMPLOYMENT_CELEX = frozenset({"32000L0078"})
_CONSUMER_CELEX = frozenset({"32011L0083", "32019L0771"})
_PRIVACY_CELEX = frozenset({"32016R0679"})
_CROSS_DOMAIN_BLOCK = _CUSTOMS_CELEX | _FINANCIAL_CELEX | _DSA_CELEX

_INTERNAL_MARKET_CELEX = frozenset({"32008R0768"})

_DOMAIN_DEFAULT_CELEX: dict[LegalRoutingDomain, str] = {
    "employment_law": "32000L0078",
    "consumer_protection": "32011L0083",
    "product_safety": "32023R0988",
    "administrative_law": "32019R1020",
    "digital_services": "32022R2065",
    "internal_market": "32008R0768",
}


def is_celex_allowed_for_domain(celex: str | None, domain: LegalRoutingDomain) -> bool:
    """Return False when CELEX belongs to an excluded legal layer for this domain."""
    if not celex or domain == "unknown":
        return True
    if domain == "digital_services":
        return celex in _DSA_CELEX
    if celex in _DSA_CELEX:
        return False
    if domain == "employment_law":
        return celex not in (_GPSR_CELEX | _SURVEILLANCE_CELEX | _CUSTOMS_CELEX | _FINANCIAL_CELEX)
    if domain == "consumer_protection":
        return celex not in (_CUSTOMS_CELEX | _FINANCIAL_CELEX | _DSA_CELEX | _EMPLOYMENT_CELEX | _GPSR_CELEX)
    if domain == "product_safety":
        return celex not in (_CUSTOMS_CELEX | _FINANCIAL_CELEX | _DSA_CELEX | _EMPLOYMENT_CELEX)
    if domain == "administrative_law":
        return celex not in (_CUSTOMS_CELEX | _FINANCIAL_CELEX | _DSA_CELEX | _EMPLOYMENT_CELEX)
    if domain == "internal_market":
        if celex in _INTERNAL_MARKET_CELEX:
            return True
        return celex not in (
            _CUSTOMS_CELEX | _FINANCIAL_CELEX | _GPSR_CELEX | _SURVEILLANCE_CELEX | _DSA_CELEX
        )
    if domain == "data_protection":
        return celex in _PRIVACY_CELEX
    return celex not in _CROSS_DOMAIN_BLOCK


def filter_instruments_by_domain(
    instruments: list[InstrumentTarget],
    domain: LegalRoutingDomain,
) -> list[InstrumentTarget]:
    """Keep only instruments whose CELEX matches the routing domain."""
    if domain == "unknown":
        return list(instruments)
    return [item for item in instruments if is_celex_allowed_for_domain(item.celex, domain)]


def default_instrument_for_domain(
    domain: LegalRoutingDomain,
    question: str,
) -> InstrumentTarget | None:
    """Safe fallback instrument when domain filter removed all targets."""
    celex = _DOMAIN_DEFAULT_CELEX.get(domain)
    if not celex:
        return None
    return InstrumentTarget(name=_default_name(domain, question.lower()), celex=celex, articles=[], confidence=0.6)


def filter_chunks_by_domain(
    chunks: list[dict[str, Any]],
    domain: LegalRoutingDomain,
) -> list[dict[str, Any]]:
    """Drop chunks from excluded CELEX layers."""
    if domain == "unknown":
        return list(chunks)
    kept = [
        chunk for chunk in chunks
        if is_celex_allowed_for_domain(str(chunk.get("celex", "")), domain)
    ]
    return kept or list(chunks)


def rank_chunk_for_domain(text: str, domain: LegalRoutingDomain) -> int:
    """Score chunk fit for domain (+2 match, -3 cross-domain noise)."""
    lowered = (text or "").lower()
    score = 0
    if domain == "employment_law" and any(m in lowered for m in ("werknemer", "discriminatie")):
        score += 2
    if domain == "consumer_protection" and any(m in lowered for m in ("consument", "herroep")):
        score += 2
    if domain == "product_safety" and any(m in lowered for m in ("fabrikant", "conformiteit", "ce ")):
        score += 2
    if domain == "administrative_law" and any(m in lowered for m in ("surveillance", "toezicht")):
        score += 2
    if domain == "internal_market" and any(m in lowered for m in ("lidstaat", "harmonisatie")):
        score += 2
    if domain == "digital_services" and "digital services" in lowered:
        score += 2
    if "digital services act" in lowered and domain != "digital_services":
        score -= 3
    if domain == "employment_law" and any(m in lowered for m in ("douane", "market abuse", "dsa")):
        score -= 3
    if domain == "internal_market" and "invoerrechten" in lowered:
        score -= 3
    return score


def rank_chunks_by_domain(
    chunks: list[dict[str, Any]],
    domain: LegalRoutingDomain,
) -> list[dict[str, Any]]:
    """Sort chunks by domain relevance."""
    if domain == "unknown":
        return list(chunks)
    scored = [
        (rank_chunk_for_domain(str(chunk.get("text", "")), domain), chunk)
        for chunk in chunks
    ]
    scored.sort(key=lambda pair: pair[0], reverse=True)
    return [chunk for _, chunk in scored]


def _default_name(domain: LegalRoutingDomain, lowered: str) -> str:
    if domain == "employment_law":
        return "equal_treatment_employment"
    if domain == "consumer_protection" and "retour" in lowered:
        return "consumer_withdrawal"
    if domain == "administrative_law":
        return "product_conformity_doc"
    if domain == "product_safety":
        return "gpsr_manufacturer_risk"
    if domain == "digital_services":
        return "dsa_obligations"
    if domain == "internal_market":
        return "internal_market_national_rules"
    return "EU-regelgeving"

"""Routing legal_domain inference — domain-first with V3 horizontal overrides."""
import re
from typing import Literal

LegalRoutingDomain = Literal[
    "internal_market",
    "consumer_protection",
    "employment_law",
    "administrative_law",
    "product_safety",
    "data_protection",
    "digital_services",
    "customs_law",
    "unknown",
]

LegalActor = Literal[
    "manufacturer", "consumer", "employee", "authority", "platform", "operator", "unknown",
]

_INTERNAL_MARKET_OVERRIDE = (
    "lidstaat", "nationale regel", "nationale regels", "afwijken", "verbieden",
    "verplicht binnen land",
)
_DSA_EXPLICIT = (
    "content moderation", "illegal content", "illegale content", "platform transparency",
    "hosting liability", "hosting aansprakelijk", "digital services act", " dsa",
    "content verwijder", "moderatie", "illegale inhoud",
)
_PRODUCT_SAFETY_HINTS = (
    " ce ", "ce-mark", "product on market", "op de markt brengen", "fabrikant",
    "manufacturer", "conformity", "conformiteit", "conformiteitsverklaring",
)
_RECALL_SAFETY_HINTS = (
    "terugroep", "terughaal", "recall", "onveilig", "veiligheidsrisico",
    "productveiligheid", "gpsr",
)
_EMPLOYEE_HINTS = (
    "werknemer", "medewerker", "ontslag", "arbeidscontract",
    "sollicitant", "sollicitatie", "werkgever",
)
_CONSUMER_HINTS = ("consument", "klant", "koper", "webshop", "retour", "herroep", "koop")
_ADMIN_HINTS = ("toezichthouder", "handhaving", "markttoezicht", "boete", "van de markt")
_PRIVACY_HINTS = ("avg", "gdpr", "persoonsgegevens", "privacy", "gegevensbescherming")
_GDPR_ENFORCEMENT = ("handhaving avg", "boete gdpr", "gegevensbeschermingsautoriteit")
_CUSTOMS_HINTS = ("douane", "customs", "invoer", "aangifte", "ucc", "invoerrechten")
_IDENTIFICATION_HINTS = ("legitim", "identif", "paspoort", "eidas", "id-kaart", "id kaart")


def infer_legal_domain(question: str, actor: LegalActor) -> LegalRoutingDomain:
    """Return one routing domain — overrides first, then actor rules, then fallback."""
    lowered = question.lower()
    if _is_explicit_dsa_question(lowered):
        return "digital_services"
    if any(h in lowered for h in _CUSTOMS_HINTS):
        return "customs_law"
    override = _apply_internal_market_override(lowered)
    if override:
        return override
    if any(h in lowered for h in _RECALL_SAFETY_HINTS):
        return "product_safety"
    product_domain = _apply_product_safety_override(lowered, actor)
    if product_domain:
        return product_domain
    hinted = _domain_from_fallback_hints(lowered)
    hinted = _sanitize_digital_services_hint(lowered, hinted)
    domain = _apply_actor_hard_rules(actor, lowered, hinted)
    if domain != "unknown":
        return domain
    return hinted or "unknown"


def _apply_internal_market_override(lowered: str) -> LegalRoutingDomain | None:
    if not any(h in lowered for h in _INTERNAL_MARKET_OVERRIDE):
        return None
    if any(h in lowered for h in ("e-commerce", "webshop", "online winkel", "vertegenwoordiger")):
        return "consumer_protection"
    if any(h in lowered for h in _GDPR_ENFORCEMENT):
        return None
    return "internal_market"


def _apply_product_safety_override(lowered: str, actor: LegalActor) -> LegalRoutingDomain | None:
    if not any(h in lowered for h in _PRODUCT_SAFETY_HINTS) and not re.search(r"\b(ce|gpsr)\b", lowered):
        return None
    if any(h in lowered for h in _INTERNAL_MARKET_OVERRIDE):
        return "internal_market"
    if actor in {"manufacturer", "operator", "unknown"}:
        return "product_safety"
    return "product_safety"


def _is_explicit_dsa_question(lowered: str) -> bool:
    return any(h in lowered for h in _DSA_EXPLICIT)


def _sanitize_digital_services_hint(
    lowered: str,
    hinted: LegalRoutingDomain,
) -> LegalRoutingDomain:
    if hinted != "digital_services" and "digital_services" not in str(hinted):
        return hinted
    return "digital_services" if _is_explicit_dsa_question(lowered) else "unknown"


def _domain_from_fallback_hints(lowered: str) -> LegalRoutingDomain:
    if any(h in lowered for h in _CUSTOMS_HINTS):
        return "customs_law"
    if any(h in lowered for h in _IDENTIFICATION_HINTS):
        return "internal_market"
    if any(h in lowered for h in _PRIVACY_HINTS):
        return "data_protection"
    if any(h in lowered for h in _EMPLOYEE_HINTS):
        return "employment_law"
    if any(h in lowered for h in _CONSUMER_HINTS):
        return "consumer_protection"
    if any(h in lowered for h in _INTERNAL_MARKET_OVERRIDE):
        return "internal_market"
    if any(h in lowered for h in _ADMIN_HINTS):
        return "administrative_law"
    if _is_explicit_dsa_question(lowered):
        return "digital_services"
    if any(h in lowered for h in _PRODUCT_SAFETY_HINTS):
        return "product_safety"
    return "unknown"


def _apply_actor_hard_rules(
    actor: LegalActor,
    lowered: str,
    hinted: LegalRoutingDomain,
) -> LegalRoutingDomain:
    if actor == "employee":
        return "employment_law"
    if actor == "consumer":
        if any(h in lowered for h in _RECALL_SAFETY_HINTS):
            return "product_safety"
        return "consumer_protection"
    if actor == "platform":
        return "digital_services" if _is_explicit_dsa_question(lowered) else hinted
    if actor == "authority":
        if any(h in lowered for h in _INTERNAL_MARKET_OVERRIDE):
            return "internal_market"
        if _is_product_enforcement_question(lowered):
            return "administrative_law"
        return "administrative_law"
    if actor in {"manufacturer", "operator"}:
        if any(h in lowered for h in _INTERNAL_MARKET_OVERRIDE):
            return "internal_market"
        return "product_safety"
    if actor == "unknown" and hinted != "unknown":
        return hinted
    return "unknown"


def _is_product_enforcement_question(lowered: str) -> bool:
    return any(h in lowered for h in _ADMIN_HINTS) and (
        "product" in lowered or "markt" in lowered
    )

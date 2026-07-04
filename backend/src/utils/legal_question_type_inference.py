"""Infer legal_question_type — third interpretation layer (V3, not used for retrieval routing)."""
import re
from typing import Literal

from backend.src.utils.legal_domain_inference import LegalActor, LegalRoutingDomain

LegalQuestionType = Literal[
    "market_access",
    "rights",
    "obligations",
    "enforcement",
    "national_measure",
    "definition",
    "unknown",
]

_DEFINITION_HINTS = ("wat is ", "wat betekent ", "definitie van ")
_ENFORCEMENT_HINTS = (
    "handhaving", "toezicht", "sanctie", "boete", "van de markt halen", "markttoezicht",
)
_OBLIGATION_HINTS = ("verplicht", "welke verplichtingen", "plicht ", "moet een bedrijf")
_RIGHTS_HINTS = ("rechten", "recht op", "welke rechten", "discriminatie", "gelijke behandeling")
_NATIONAL_MEASURE_HINTS = (
    "lidstaat", "nationale regel", "nationale regels", "afwijken", "verbieden",
    "verplicht binnen land",
)
_PRODUCT_ACCESS_HINTS = (
    "ce-mark", " ce ", "op de markt brengen", "product op market", "conformity", "conformiteit",
)


def infer_legal_question_type(
    question: str,
    actor: LegalActor,
    domain: LegalRoutingDomain,
) -> LegalQuestionType:
    """Classify question type from text + actor/domain context."""
    lowered = question.lower()
    if domain == "internal_market" and _matches_any(lowered, _NATIONAL_MEASURE_HINTS):
        return "national_measure"
    if _matches_any(lowered, _DEFINITION_HINTS):
        return "definition"
    if _matches_any(lowered, _ENFORCEMENT_HINTS) or domain == "administrative_law":
        if "mag" in lowered or "wanneer" in lowered:
            return "enforcement"
    if actor in {"employee", "consumer"} and _matches_any(lowered, _RIGHTS_HINTS):
        return "rights"
    if actor == "employee":
        return "rights"
    if actor == "consumer" and re.search(r"\bmag\b", lowered):
        return "rights"
    if _matches_any(lowered, _OBLIGATION_HINTS):
        return "obligations"
    if actor in {"manufacturer", "operator"} and _matches_any(lowered, _PRODUCT_ACCESS_HINTS):
        return "market_access"
    if re.search(r"\bmag\b", lowered) and domain == "product_safety":
        return "market_access"
    return "unknown"


def _matches_any(text: str, hints: tuple[str, ...]) -> bool:
    return any(hint in text for hint in hints)

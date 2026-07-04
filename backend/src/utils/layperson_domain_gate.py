"""Reject layperson answers from wrong legal domain or bad openings (V3)."""
import re

from backend.src.utils.legal_domain_inference import LegalActor, LegalRoutingDomain
from backend.src.utils.legal_domain_retrieval_filter import is_celex_allowed_for_domain
from backend.src.utils.legal_question_type_inference import LegalQuestionType
from backend.src.utils.layperson_actor_gate import answer_starts_with_legal_dump

_DSA_CELEX = frozenset({"32022R2065"})
_MARKET_ACCESS_FRAMING = (
    "market surveillance authorities",
    "markttoezichtautoriteit",
    "member states shall ensure",
    "lidstaten zorgen ervoor",
)
_ENFORCEMENT_NOISE = (
    "douaneautoriteit", "douaneregeling", "informatie- en communicatiesysteem",
)
_ENFORCEMENT_SIGNALS = (
    "markttoezicht", "non-conform", "terugroep", "van de markt", "withdrawal",
)
_BOILERPLATE_OPENERS = (
    "op basis van de eu-regelgeving die voor uw vraag geldt",
    "this directive shall",
    "member states shall",
)
_BARE_JA = re.compile(r"^\s*\*\*ja\.?\*\*", re.IGNORECASE)
_CONDITION_WORDS = re.compile(
    r"\b(niet|nee|alleen|onder voorwaarden|in principe|tenzij|meestal|uitzondering|hangt af)\b",
    re.IGNORECASE,
)
_TYPES_NEEDING_CONDITIONS = frozenset({"market_access", "rights", "obligations"})


def is_weak_kort_antwoord(kort: str) -> bool:
    """True when kort antwoord is only 'Ja' or unconditional Ja without nuance."""
    stripped = kort.strip()
    if _BARE_JA.match(stripped) and not _CONDITION_WORDS.search(stripped):
        return True
    if stripped.lower() in {"ja.", "ja", "**ja.**", "**ja**"}:
        return True
    return False


def answer_starts_with_boilerplate(answer: str) -> bool:
    """True when kort antwoord opens with copy-paste EU boilerplate."""
    kort = _kort_section(answer).lower()
    return any(opener in kort for opener in _BOILERPLATE_OPENERS)


def is_wrong_domain_answer(
    answer: str,
    actor: LegalActor,
    domain: LegalRoutingDomain,
    citation_celexes: list[str] | None = None,
    question_type: LegalQuestionType = "unknown",
) -> bool:
    """True when answer uses wrong legal layer or forbidden framing."""
    if not answer.strip():
        return False
    if answer_starts_with_legal_dump(answer) or answer_starts_with_boilerplate(answer):
        return True
    kort = _kort_section(answer)
    if is_weak_kort_antwoord(kort):
        return True
    if question_type in _TYPES_NEEDING_CONDITIONS and is_weak_kort_antwoord(kort):
        return True
    if actor in {"employee", "consumer"} and _has_market_access_framing(answer):
        return True
    if domain != "digital_services" and _mentions_dsa(answer, citation_celexes):
        return True
    if domain == "internal_market" and _uses_blocked_internal_market_sources(citation_celexes):
        return True
    if domain == "administrative_law" and _has_financial_markers(answer):
        return True
    if question_type == "enforcement" and _enforcement_answer_has_wrong_chunk(kort):
        return True
    if citation_celexes and domain != "unknown":
        blocked = [
            celex for celex in citation_celexes
            if celex and not is_celex_allowed_for_domain(celex, domain)
        ]
        if blocked:
            return True
    return False


def _enforcement_answer_has_wrong_chunk(kort: str) -> bool:
    lowered = kort.lower()
    has_noise = any(marker in lowered for marker in _ENFORCEMENT_NOISE)
    has_signal = any(marker in lowered for marker in _ENFORCEMENT_SIGNALS)
    return has_noise and not has_signal


def _mentions_dsa(answer: str, citation_celexes: list[str] | None) -> bool:
    if citation_celexes and any(celex in _DSA_CELEX for celex in citation_celexes):
        return True
    lowered = answer.lower()
    return "digital services act" in lowered or " dsa " in lowered


def _uses_blocked_internal_market_sources(citation_celexes: list[str] | None) -> bool:
    if not citation_celexes:
        return False
    blocked = {"32013R0952", "32015R2446", "32022R2065", "32014R0596"}
    return any(celex in blocked for celex in citation_celexes)


def _has_market_access_framing(text: str) -> bool:
    lowered = text.lower()
    return any(marker in lowered for marker in _MARKET_ACCESS_FRAMING)


def _has_financial_markers(text: str) -> bool:
    lowered = text.lower()
    return "marktmisbruik" in lowered or "financial instrument" in lowered


def _kort_section(text: str) -> str:
    for marker in (
        "## kort antwoord",
        "## wat betekent dit in de praktijk?",
        "## uitleg",
        "## voorbeeld",
        "## juridische basis",
    ):
        idx = text.lower().find(marker)
        if idx >= 0:
            start = idx + len(marker)
            rest = text[start:].lstrip(":\n")
            end = rest.lower().find("\n##")
            return rest[: end if end > 0 else 600]
    return text[:600]

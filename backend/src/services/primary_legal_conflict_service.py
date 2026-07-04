"""Select exactly one primary legal conflict — V4 juridische hersenen."""
import re

from shared.schemas.legal_conflict import PrimaryLegalConflict
from shared.schemas.legal_hypothesis import LegalHypothesis

_DSA_HINTS = (
    "digital services act", " dsa", "content moderation", "illegale content",
    "platform transparency", "illegal content",
)
_GDPR_HINTS = ("avg", "gdpr", "persoonsgegevens", "gegevensbescherming", "privacy")
_EMPLOYMENT_HINTS = (
    "werknemer", "werkgever", "sollicitant", "sollicitatie", "ontslag",
    "arbeidsovereenkomst", "discriminatie", "langdurig ziek",
)
_ENFORCEMENT_HINTS = (
    "toezichthouder", "markttoezicht", "van de markt", "handhaving", "sanctie",
)
_PRODUCT_HINTS = (
    "ce-mark", "ce marking", " fabrikant", "gpsr", "conformiteit", "product op de markt",
)
_INTERNAL_MARKET_HINTS = (
    "lidstaat", "lidstaten", "nationale regel", "nationale maatregel",
    "afwijken", "afwijking", "e-commerce", "webshop", "vertegenwoordiger",
    "country of origin", "interne markt",
)
_CONSUMER_HINTS = ("consument", "retour", "herroep", "koop op afstand", "webshop koop")


def select_primary_legal_conflict(
    question: str,
    hypothesis: LegalHypothesis,
) -> PrimaryLegalConflict:
    """Pick exactly one primary conflict; supporting domains never become primary."""
    lowered = question.lower()
    if _matches(lowered, _DSA_HINTS):
        return "platform_governance_issue"
    if _matches(lowered, _GDPR_HINTS) and not _matches(lowered, _EMPLOYMENT_HINTS):
        return "data_processing_issue"
    if _matches(lowered, _EMPLOYMENT_HINTS):
        return "employment_relationship_issue"
    if _matches(lowered, _ENFORCEMENT_HINTS) and "product" in lowered:
        return "administrative_enforcement_issue"
    if _matches(lowered, _PRODUCT_HINTS):
        return "product_compliance_issue"
    if _is_internal_market_conflict(lowered):
        return "internal_market_restriction"
    if _matches(lowered, _CONSUMER_HINTS):
        return "consumer_transaction_issue"
    return _fallback_from_hypothesis(hypothesis)


def infer_parties(question: str) -> list[str]:
    """Extract party labels mentioned in the question."""
    lowered = question.lower()
    parties: list[str] = []
    for label, hints in (
        ("lidstaat", ("lidstaat", "lidstaten")),
        ("werkgever", ("werkgever",)),
        ("werknemer", ("werknemer", "sollicitant")),
        ("consument", ("consument",)),
        ("fabrikant", ("fabrikant", "producent")),
        ("toezichthouder", ("toezichthouder",)),
        ("platform", ("platform",)),
    ):
        if any(h in lowered for h in hints):
            parties.append(label)
    return parties[:6]


def infer_context(question: str) -> str:
    """Short context tag for the legal situation."""
    lowered = question.lower()
    if "sollicit" in lowered:
        return "sollicitatie / pre-employment"
    if "e-commerce" in lowered or "webshop" in lowered:
        return "e-commerce / online verkoop"
    if "lidstaat" in lowered:
        return "lidstaatmaatregel / interne markt"
    if "consument" in lowered:
        return "consumententransactie"
    if "ontslag" in lowered or "werknemer" in lowered:
        return "arbeidsrelatie"
    return "EU-recht algemeen"


def _is_internal_market_conflict(lowered: str) -> bool:
    has_state = any(h in lowered for h in ("lidstaat", "lidstaten", "eu-lidstaat"))
    has_restriction = any(h in lowered for h in (
        "eisen", "verplicht", "afwijken", "nationale", "e-commerce", "webshop", "vertegenwoordiger",
    ))
    return has_state and has_restriction


def _matches(lowered: str, hints: tuple[str, ...]) -> bool:
    return any(h in lowered for h in hints)


def _fallback_from_hypothesis(hypothesis: LegalHypothesis) -> PrimaryLegalConflict:
    domain_map: dict[str, PrimaryLegalConflict] = {
        "internal_market": "internal_market_restriction",
        "consumer_protection": "consumer_transaction_issue",
        "employment_law": "employment_relationship_issue",
        "data_protection": "data_processing_issue",
        "product_safety": "product_compliance_issue",
        "administrative_law": "administrative_enforcement_issue",
        "digital_services": "platform_governance_issue",
    }
    return domain_map.get(hypothesis.legal_domain_guess, "consumer_transaction_issue")

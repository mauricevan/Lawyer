"""Select exactly one primary legal conflict — V4 juridische hersenen."""
import re

from backend.src.utils.clarification_patterns import IDENTIFICATION_HINTS
from shared.schemas.legal_conflict import PrimaryLegalConflict
from shared.schemas.legal_hypothesis import LegalHypothesis

_DSA_HINTS = (
    "digital services act", "dsa", "content moderation", "illegale content",
    "platform transparency", "illegal content", "hosting", "intermediary",
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
_REGISTRATION_HINTS = ("registr", "aanmel", "melden", "aanmelden")
_DIGITAL_PRODUCT_HINTS = (
    "chatbot", "ai-assistent", " bot", "plugin", "widget", "saas", "app / saas",
    "software as a service", "ai-chatbot", "ai tool", "ai-tool", "extensie",
)
_PLATFORM_START_HINTS = (
    "platform beginnen", "platform starten", "nieuw platform", "mag ik een platform",
    "marktplaats", "contentwebsite",
)
_CUSTOMS_HINTS = (
    "douane", "customs", "invoer", "import", "aangifte", "ucc", "douanewetboek",
    "invoerrechten", "invoer aangifte", "vanuit china", "derde land",
)
_DATA_STORAGE_HINTS = (
    "data opslaan", "gegevens opslaan", "data bewaren", "gegevens bewaren",
    "persoonsgegeven", "klantgegevens", "data van klanten", "gegevens van klanten",
)
_PERSONAL_DATA_HINTS = (
    "e-mail", "email", "telefoonnummer", "adresgegevens", "ip-adres",
    "persoonsgegeven", "persoonsgegevens",
)
_DATA_SHARING_HINTS = (
    "doorgeven", "delen", "verstrekken", "doorgifte", "reclame", "marketing",
    "nieuwsbrief", "adverteren",
)


def select_primary_legal_conflict(
    question: str,
    hypothesis: LegalHypothesis,
) -> PrimaryLegalConflict:
    """Pick exactly one primary conflict; supporting domains never become primary."""
    lowered = question.lower()
    if _matches(lowered, _DSA_HINTS):
        return "platform_governance_issue"
    if _matches(lowered, _PLATFORM_START_HINTS):
        return "platform_governance_issue"
    if _matches(lowered, _CUSTOMS_HINTS):
        return "customs_import_issue"
    if _matches(lowered, IDENTIFICATION_HINTS) or _matches(lowered, ("eidas", "kyc", "paspoort", "id-kaart")):
        return "identity_verification_issue"
    if _matches(lowered, _DATA_STORAGE_HINTS) or (
        _matches(lowered, ("data", "gegevens")) and _matches(lowered, ("opslaan", "bewaren", "verwerken"))
    ):
        return "data_processing_issue"
    if _matches(lowered, _PERSONAL_DATA_HINTS) and _matches(lowered, _DATA_SHARING_HINTS):
        return "data_processing_issue"
    if _matches(lowered, _GDPR_HINTS) and not _matches(lowered, _EMPLOYMENT_HINTS):
        return "data_processing_issue"
    if _matches(lowered, _EMPLOYMENT_HINTS):
        return "employment_relationship_issue"
    if _is_registration_digital_product_conflict(lowered):
        return "product_compliance_issue"
    if _matches(lowered, _ENFORCEMENT_HINTS) and "product" in lowered:
        return "administrative_enforcement_issue"
    if _matches(lowered, _PRODUCT_HINTS):
        return "product_compliance_issue"
    if _matches(lowered, ("terugroep", "terughaal", "recall", "veiligheidsrisico")):
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


def _is_registration_digital_product_conflict(lowered: str) -> bool:
    """§5 G3: chatbot/app/SaaS registration → GPSR product compliance, not DSA platform."""
    has_reg = _matches(lowered, _REGISTRATION_HINTS)
    has_product = _matches(lowered, _DIGITAL_PRODUCT_HINTS)
    has_platform_start = _matches(lowered, _PLATFORM_START_HINTS)
    return has_reg and has_product and not has_platform_start


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
        "customs_law": "customs_import_issue",
    }
    return domain_map.get(hypothesis.legal_domain_guess, "consumer_transaction_issue")

"""Infer legal actor and issue from question text (pre-retrieval, domain-agnostic)."""
import re
from typing import Literal

LegalActor = Literal[
    "manufacturer", "consumer", "employee", "authority", "platform", "operator", "unknown",
]
LegalIssue = Literal[
    "market_access", "obligation", "enforcement", "rights", "definition", "unknown",
]

_EMPLOYEE_HINTS = (
    "werknemer", "werknemers", "medewerker", "medewerkers", "arbeidscontract",
    "ontslagen", "ontslag", "werkgever ontslaat", "langdurig ziek", "ziekteverlof",
)
_MANUFACTURER_HINTS = (
    "fabrikant", "producent", "bedrijf", "ondernemer", "verkoper", "importeur",
    "importeert", "inverkeerbrenger",
)
_CONSUMER_HINTS = (
    "consument", "klant", "koper", "gebruiker", "passagier", "ik koop", "webshop",
)
_PLATFORM_HINTS = (
    "content moderation", "illegal content", "illegale content", "hosting liability",
    "digital services act", " dsa", "content verwijder",
)
_AUTHORITY_HINTS = (
    "toezichthouder", "autoriteit", "handhaving", "inspectie", "boete",
    "markttoezicht", "douane", "nvwa", "lidstaat", "lidstaten", "member state",
)
_DEFINITION_HINTS = ("wat is ", "wat betekent ", "definitie van ", "uitleg van ")
_ENFORCEMENT_HINTS = (
    "handhaving", "toezicht", "sanctie", "boete", "in beslag", "terugroeping door",
    "autoriteit moet", "autoriteiten moeten", "market surveillance",
)
_OBLIGATION_HINTS = (
    "verplicht", "moet ik", "moet een", "welke verplichtingen", "plicht ",
)
_RIGHTS_HINTS = (
    "rechten", "recht op", "welke rechten", "kan ik aanspraak", "aanspraak maken",
)
_DISCRIMINATION_HINTS = (
    "discriminatie", "gelijke behandeling", "ongelijke behandeling", "handicap",
    "gezondheidstoestand",
)
_MARKET_ACCESS_HINTS = (
    "mag ik", "mag een", "mag mijn", "wanneer mag", "zonder ", "toegestaan",
    "op de markt brengen", "markt brengen", "inverkeerbrengen", "ce-markering",
    "ce marking", " gpsr", " product op de markt",
)
_CE_MARKET_ACCESS_HINTS = (
    "ce-markering", "ce marking", " ce ", "ce-mark", "op de markt brengen",
    "markt brengen", "inverkeerbrengen", "zonder ce", "mag een bedrijf",
    "harmonisatiewetgeving", "conformiteitsverklaring",
)


def infer_legal_actor(question: str) -> LegalActor:
    """Return primary legal actor implied by the question."""
    lowered = question.lower()
    if any(h in lowered for h in _EMPLOYEE_HINTS):
        return "employee"
    if any(h in lowered for h in _PLATFORM_HINTS):
        return "platform"
    if any(h in lowered for h in _AUTHORITY_HINTS) and not _asks_as_private_party(lowered):
        return "authority"
    if "exploitant" in lowered:
        return "operator"
    if any(h in lowered for h in _MANUFACTURER_HINTS):
        return "manufacturer"
    if any(h in lowered for h in _CONSUMER_HINTS):
        return "consumer"
    if _asks_as_private_party(lowered):
        return _resolve_mag_ik_actor(lowered)
    return "unknown"


def infer_legal_issue(question: str) -> LegalIssue:
    """Return primary legal issue type implied by the question."""
    lowered = question.lower()
    if any(h in lowered for h in _DEFINITION_HINTS):
        return "definition"
    if any(h in lowered for h in _ENFORCEMENT_HINTS):
        return "enforcement"
    if any(h in lowered for h in _MARKET_ACCESS_HINTS):
        return "market_access"
    if any(h in lowered for h in _OBLIGATION_HINTS):
        return "obligation"
    if any(h in lowered for h in _RIGHTS_HINTS):
        return "rights"
    if any(h in lowered for h in _DISCRIMINATION_HINTS):
        return "rights"
    return "unknown"


def infer_legal_context(question: str) -> tuple[LegalActor, LegalIssue]:
    """Infer actor + issue including CE/market-access fallback."""
    actor = infer_legal_actor(question)
    issue = infer_legal_issue(question)
    return apply_market_access_fallback(question, actor, issue)


def apply_market_access_fallback(
    question: str,
    actor: LegalActor,
    issue: LegalIssue,
) -> tuple[LegalActor, LegalIssue]:
    """Fallback when planner fails: CE / placing-on-market → manufacturer + market_access."""
    lowered = question.lower()
    if not _is_ce_market_access_question(lowered):
        return actor, issue
    resolved_actor: LegalActor = actor if actor != "unknown" else "manufacturer"
    resolved_issue: LegalIssue = (
        "market_access" if issue in {"unknown", "obligation"} else issue
    )
    return resolved_actor, resolved_issue


def _is_ce_market_access_question(lowered: str) -> bool:
    if any(hint in lowered for hint in _CE_MARKET_ACCESS_HINTS):
        return True
    return bool(re.search(r"\b(ce|gpsr)\b", lowered)) and (
        "markt" in lowered or "product" in lowered or "fabrikant" in lowered
    )


def _asks_as_private_party(lowered: str) -> bool:
    return bool(re.search(r"\bmag (ik|een bedrijf|een fabrikant|mijn bedrijf|ik mijn)\b", lowered))


def _resolve_mag_ik_actor(lowered: str) -> LegalActor:
    if any(h in lowered for h in _EMPLOYEE_HINTS):
        return "employee"
    if any(h in lowered for h in ("bedrijf", "fabrikant", "producent", "importeur")):
        return "manufacturer"
    if any(h in lowered for h in _CONSUMER_HINTS):
        return "consumer"
    return "consumer"

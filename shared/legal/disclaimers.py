"""Central legal disclaimers and escalation copy for API responses."""
from typing import Literal

Audience = Literal["layperson", "professional"]

DISCLAIMER_LAYPERSON = (
    "Dit is algemene informatie op basis van EUR-Lex, geen persoonlijk juridisch advies. "
    "Bij twijfel: raadpleeg een advocaat."
)

DISCLAIMER_PROFESSIONAL = (
    "Dit is geen juridisch advies. Controleer altijd de bron op EUR-Lex en "
    "verifieer de toepasselijke versie en inwerkingtreding."
)

ESCALATION_LAYPERSON = (
    "Voor bindend advies over uw specifieke situatie kunt u een advocaat of "
    "juridisch adviseur raadplegen."
)

ESCALATION_PROFESSIONAL = (
    "Voor dossier-specifieke interpretatie: escaleer naar een gekwalificeerde jurist "
    "of uw compliance officer."
)


def get_disclaimer(audience: Audience = "layperson") -> str:
    if audience == "professional":
        return DISCLAIMER_PROFESSIONAL
    return DISCLAIMER_LAYPERSON


def get_escalation_text(audience: Audience = "layperson") -> str:
    if audience == "professional":
        return ESCALATION_PROFESSIONAL
    return ESCALATION_LAYPERSON

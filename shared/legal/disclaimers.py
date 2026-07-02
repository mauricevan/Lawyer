"""Central legal disclaimers and escalation copy for API responses."""
from typing import Literal

Audience = Literal["layperson", "professional"]
Language = Literal["nl", "en", "fr", "de", "es"]

_DISCLAIMERS: dict[str, dict[Audience, str]] = {
    "nl": {
        "layperson": (
            "Dit is algemene informatie op basis van EUR-Lex, geen persoonlijk juridisch advies. "
            "Bij twijfel: raadpleeg een advocaat."
        ),
        "professional": (
            "Dit is geen juridisch advies. Controleer altijd de bron op EUR-Lex en "
            "verifieer de toepasselijke versie en inwerkingtreding."
        ),
    },
    "en": {
        "layperson": (
            "This is general information based on EUR-Lex, not personal legal advice. "
            "When in doubt, consult a lawyer."
        ),
        "professional": (
            "This is not legal advice. Always verify the source on EUR-Lex and "
            "confirm the applicable version and entry into force."
        ),
    },
    "fr": {
        "layperson": (
            "Ceci est une information générale basée sur EUR-Lex, pas un conseil juridique personnel. "
            "En cas de doute, consultez un avocat."
        ),
        "professional": (
            "Ceci n'est pas un avis juridique. Vérifiez toujours la source sur EUR-Lex et "
            "la version applicable ainsi que son entrée en vigueur."
        ),
    },
    "de": {
        "layperson": (
            "Dies sind allgemeine Informationen auf Basis von EUR-Lex, keine persönliche Rechtsberatung. "
            "Im Zweifel wenden Sie sich an einen Anwalt."
        ),
        "professional": (
            "Dies ist keine Rechtsberatung. Prüfen Sie stets die Quelle auf EUR-Lex sowie "
            "die anwendbare Fassung und ihr Inkrafttreten."
        ),
    },
    "es": {
        "layperson": (
            "Esta es información general basada en EUR-Lex, no asesoramiento jurídico personal. "
            "En caso de duda, consulte a un abogado."
        ),
        "professional": (
            "Esto no es asesoramiento jurídico. Verifique siempre la fuente en EUR-Lex y "
            "la versión aplicable y su entrada en vigor."
        ),
    },
}

_ESCALATIONS: dict[str, dict[Audience, str]] = {
    "nl": {
        "layperson": (
            "Voor bindend advies over uw specifieke situatie kunt u een advocaat of "
            "juridisch adviseur raadplegen."
        ),
        "professional": (
            "Voor dossier-specifieke interpretatie: escaleer naar een gekwalificeerde jurist "
            "of uw compliance officer."
        ),
    },
    "en": {
        "layperson": "For binding advice on your situation, consult a qualified lawyer.",
        "professional": "For case-specific interpretation, escalate to qualified counsel or compliance.",
    },
    "fr": {
        "layperson": "Pour un avis contraignant, consultez un avocat qualifié.",
        "professional": "Pour une interprétation spécifique au dossier, escaladez vers un juriste qualifié.",
    },
    "de": {
        "layperson": "Für verbindliche Beratung wenden Sie sich an einen qualifizierten Anwalt.",
        "professional": "Für fallbezogene Auslegung eskalieren Sie an qualifizierte Juristen oder Compliance.",
    },
    "es": {
        "layperson": "Para asesoramiento vinculante, consulte a un abogado cualificado.",
        "professional": "Para interpretación específica del caso, escale a un jurista o compliance cualificado.",
    },
}


def get_disclaimer(audience: Audience = "layperson", language: str = "nl") -> str:
    lang = language.lower().split("-")[0]
    bundle = _DISCLAIMERS.get(lang, _DISCLAIMERS["nl"])
    return bundle[audience]


def get_escalation_text(audience: Audience = "layperson", language: str = "nl") -> str:
    lang = language.lower().split("-")[0]
    bundle = _ESCALATIONS.get(lang, _ESCALATIONS["nl"])
    return bundle[audience]

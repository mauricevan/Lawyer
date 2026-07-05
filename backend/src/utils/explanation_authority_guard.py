"""Fail-fast detection of pseudo-judicial language in user-facing explanations."""
import re

_FORBIDDEN_HEADINGS = (
    "hof-simulatie",
    "eu besluitvorming",
    "doctrine-evolutie",
    "doctrine-ankers",
    "doctrine-stabiliteit",
    "majority opinion",
    "advocate general",
    "court deliberation",
    "final judgment",
    "authoritative conclusion",
    "case law consistency score",
    "juridisch effect",
    "legal effect classification",
)

_FORBIDDEN_PHRASES = (
    r"\bmajority opinion\b",
    r"\badvocate general\b",
    r"\bfinal judgment\b",
    r"\bauthoritative conclusion\b",
    r"\bscore:\s*\d+/100\b",
    r"\bconfidence\s*=",
    r"\bcommission v member state\b",
    r"\bthe measure constitutes\b",
    r"\bincompatible with article \d+ tfeu\b",
    r"\bjustified and proportionate restriction\b",
)

_GAP_ANSWER = (
    "## Kort antwoord\n"
    "Ik kan op basis van de beschikbare EU-bronnen geen betrouwbaar antwoord geven.\n\n"
    "## Onzekerheden\n"
    "Het gegenereerde antwoord bevatte niet-toegestane inhoud en is geblokkeerd.\n\n"
    "## Wat u wél kunt doen\n"
    "- Formuleer uw vraag concreter en probeer opnieuw.\n"
    "- Raadpleeg [EUR-Lex](https://eur-lex.europa.eu/) of een gekwalificeerd jurist."
)


def has_authority_leak(text: str) -> bool:
    """Return True when pseudo-judicial headings or phrases are present."""
    if not text.strip():
        return False
    lower = text.lower()
    if any(heading in lower for heading in _FORBIDDEN_HEADINGS):
        return True
    return any(re.search(pattern, lower) for pattern in _FORBIDDEN_PHRASES)


def gap_answer_for_authority_leak() -> str:
    """Deterministic gap template — no legal conclusion."""
    return _GAP_ANSWER

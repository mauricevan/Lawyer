"""Detect layperson answers with wrong legal actor or copy-paste legal dumps."""
import re

from backend.src.utils.legal_question_interpretation import LegalActor, LegalIssue

_PRIVATE_ACTORS = frozenset({"manufacturer", "consumer", "operator", "employee"})
_AUTHORITY_PHRASES = (
    "market surveillance authorit",
    "markttoezichtautoriteit",
    "member states shall ensure",
    "lidstaten zorgen ervoor",
    "competent authority shall",
    "market surveillance authorities shall",
)
_LEGAL_DUMP_START = re.compile(
    r"^\s*(this directive shall apply|this directive shall|deze richtlijn shall|"
    r"market surveillance|member states shall|the commission shall|lidstaten)\b",
    re.IGNORECASE,
)


def answer_starts_with_legal_dump(answer: str) -> bool:
    """True when kort antwoord opens with raw legal boilerplate."""
    kort = _kort_section(answer)
    if _LEGAL_DUMP_START.search(kort):
        return True
    if " shall " in kort.lower() and not re.search(r"\b(ja|nee|niet altijd|in principe)\b", kort, re.I):
        return True
    return False


def is_wrong_actor_answer(answer: str, actor: LegalActor, issue: LegalIssue) -> bool:
    """True when a private-party question gets an authority/enforcement-centred answer."""
    if not answer.strip():
        return False
    if answer_starts_with_legal_dump(answer):
        return True
    if actor not in _PRIVATE_ACTORS or issue == "enforcement":
        return False
    body = answer.lower()
    hits = sum(1 for phrase in _AUTHORITY_PHRASES if phrase in body)
    if hits == 0:
        return False
    kort = _kort_section(body)
    if any(phrase in kort for phrase in _AUTHORITY_PHRASES):
        return True
    if actor == "manufacturer" and issue == "market_access" and hits >= 1:
        return True
    return hits >= 2


def _kort_section(text: str) -> str:
    for marker in (
        "## wat betekent dit in de praktijk?",
        "## uitleg",
        "## voorbeeld",
        "## juridische basis",
    ):
        idx = text.lower().find(marker)
        if idx > 0:
            return text[:idx]
    return text[:600]

"""Filter ILCL chips — answers only, never full verification questions."""
import re

_QUESTION_START = re.compile(
    r"^(waar|welke|hoe|in welk|wat voor soort|gaat het|kunt u)\b",
    re.IGNORECASE,
)
_MAX_WORDS = 8
_MAX_LEN = 80


def is_valid_layperson_chip(label: str) -> bool:
    """True when a chip is a short answer label, not a follow-up question."""
    text = label.strip()
    if not text or len(text) > _MAX_LEN:
        return False
    if "?" in text:
        return False
    if _QUESTION_START.search(text):
        return False
    if len(text.split()) > _MAX_WORDS:
        return False
    return True


def filter_layperson_chips(options: list[str]) -> list[str]:
    """Keep only answer-style chip labels."""
    seen: set[str] = set()
    filtered: list[str] = []
    for option in options:
        cleaned = option.strip()
        if not cleaned or cleaned in seen:
            continue
        if not is_valid_layperson_chip(cleaned):
            continue
        seen.add(cleaned)
        filtered.append(cleaned)
    return filtered[:5]

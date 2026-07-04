"""Sanitize LLM answer text for layperson and professional audiences."""
import re

_CELEX_CODE = re.compile(r"\b320\d{2}[RL]\d{4}\b", re.IGNORECASE)
_CELEX_LABEL = re.compile(r"CELEX:\s*\S+", re.IGNORECASE)
_NONE_ARTICLE_PATTERNS = (
    re.compile(r"\bartikel\s+None\b", re.IGNORECASE),
    re.compile(r"\barticle\s+None\b", re.IGNORECASE),
    re.compile(r"\bArt\.\s*None\b", re.IGNORECASE),
    re.compile(r"\bart\.\s*None\b", re.IGNORECASE),
)
_WEAK_ARTICLE_PATTERNS = (
    re.compile(r"lijkt artikel\s*\(onbekend\)\s*relevant", re.IGNORECASE),
    re.compile(r"lijkt artikel\s+[\w() ]+\s*relevant", re.IGNORECASE),
    re.compile(r"Op basis van [^\n]+ lijkt artikel", re.IGNORECASE),
)


def sanitize_answer_text(answer_text: str, audience: str = "layperson") -> str:
    if not answer_text:
        return answer_text
    cleaned = answer_text
    for pattern in _NONE_ARTICLE_PATTERNS:
        if audience == "professional":
            cleaned = pattern.sub("Art. (onbekend)", cleaned)
        else:
            cleaned = pattern.sub("", cleaned)
    for pattern in _WEAK_ARTICLE_PATTERNS:
        cleaned = pattern.sub("zijn de regels hier relevant", cleaned)
    if audience == "layperson":
        cleaned = _CELEX_LABEL.sub("", cleaned)
        cleaned = _CELEX_CODE.sub("", cleaned)
        cleaned = re.sub(r"Skip to main content", "", cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r"EUR-Lex CELEX[^\n]*", "", cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r"eu/resource/cellar/\S+", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"[ \t]{2,}", " ", cleaned)
    cleaned = re.sub(r" —\s*(\n|$)", r"\1", cleaned)
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)
    return cleaned.strip()

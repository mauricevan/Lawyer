"""Trim legal preamble noise from chunk text for LLM context."""
import re

_ARTICLE_START = re.compile(r"(?i)\b(artikel|article|art\.)\s*\d")


def trim_legal_preamble(text: str, max_length: int = 1500) -> str:
    if not text:
        return ""
    match = _ARTICLE_START.search(text)
    trimmed = text[match.start() :] if match and match.start() > 80 else text
    return trimmed[:max_length].strip()

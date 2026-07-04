"""Extract article numbers from chunk metadata or text."""
import re

_ARTICLE_RE = re.compile(r"(?i)(?:artikel|article|art\.)\s*(\d+[a-z]?(?:\(\d+\))?)")


def resolve_article_number(chunk: dict) -> str | None:
    for key in ("article_number", "article_ref"):
        value = chunk.get(key)
        if value:
            return str(value)
    text = str(chunk.get("text", ""))
    match = _ARTICLE_RE.search(text)
    return match.group(1) if match else None

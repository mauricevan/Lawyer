"""Shared checks for usable EUR-Lex legal text (IL-001)."""
import re

NAVIGATION_MARKERS = (
    "skip to main content",
    "my eur-lex",
    "sign in",
    "register",
    "javascript:",
    "click here",
    "please wait",
    "just a moment",
    "log in",
    "eu/resource/cellar",
    "eur-lex celex",
    "| body",
)
MIN_LEGAL_TEXT_CHARS = 500
MIN_CHUNK_TEXT_CHARS = 80
_HTML_TAG_RE = re.compile(r"<[^>]+>")


def strip_html_tags(text: str) -> str:
    cleaned = _HTML_TAG_RE.sub(" ", text)
    return re.sub(r"\s+", " ", cleaned).strip()


def is_usable_chunk_text(text: str) -> bool:
    stripped = strip_html_tags(text) if "<" in text else text.strip()
    if len(stripped) < MIN_CHUNK_TEXT_CHARS:
        return False
    lowered = stripped.lower()
    return not any(marker in lowered for marker in NAVIGATION_MARKERS)


def is_usable_legal_text(text: str) -> bool:
    stripped = strip_html_tags(text) if "<" in text else text.strip()
    if len(stripped) < MIN_LEGAL_TEXT_CHARS:
        return False
    lowered = stripped.lower()
    if any(marker in lowered for marker in NAVIGATION_MARKERS):
        return False
    return True


def usable_score(text: str) -> float:
    stripped = strip_html_tags(text) if "<" in text else text.strip()
    if not is_usable_chunk_text(text):
        return 0.0
    score = min(0.7, len(stripped) / 2500.0)
    if re.search(r"\b(artikel|article|hoofdstuk|chapter|bijlage)\b", stripped, re.I):
        score += 0.2
    if re.search(r"\b\d{4}\b", stripped):
        score += 0.1
    return min(1.0, score)


def is_usable_content_bytes(content: bytes) -> bool:
    if len(content) < 500:
        return False
    head = content[:8000].lower()
    if b"please wait" in head or b"just a moment" in head:
        return False
    if content.lstrip()[:5] == b"<?xml":
        return len(content) >= 4000
    if b"<" not in content[:500]:
        return False
    text = content.decode("utf-8", errors="ignore")
    lowered = text.lower()
    legal_signals = (
        "eli-subdivision",
        "artikel ",
        "article ",
        "hoofdstuk",
        "chapter ",
        "considérant",
        "considering that",
    )
    if any(signal in lowered for signal in legal_signals):
        return True
    if len(content) < 4000:
        return False
    mid_start = max(0, len(text) // 4)
    mid_sample = text[mid_start : mid_start + 8000]
    return is_usable_legal_text(mid_sample)

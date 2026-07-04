"""Validate retrieval chunks before persisting to live_cache or Redis."""
import logging

from backend.src.security.ssrf_guard import SecurityValidationError, validate_celex

logger = logging.getLogger(__name__)

MIN_CHUNK_TEXT_LEN = 40
BANNED_TOKENS = ("misschien",)


def is_cacheable_chunk(chunk: dict, question: str = "") -> bool:
    celex = chunk.get("celex")
    if not celex:
        return False
    try:
        validate_celex(str(celex))
    except SecurityValidationError:
        logger.debug("Skipping cache for invalid CELEX: %s", celex)
        return False
    text = str(chunk.get("text", ""))
    if len(text) < MIN_CHUNK_TEXT_LEN:
        return False
    lowered = text.lower()
    if any(token in lowered for token in BANNED_TOKENS):
        return False
    if chunk.get("source") == "live_fallback" and question:
        if _is_irrelevant_live_chunk(question, chunk):
            return False
    return True


def filter_cacheable_chunks(chunks: list[dict], question: str = "") -> list[dict]:
    return [chunk for chunk in chunks if is_cacheable_chunk(chunk, question)]


def _is_irrelevant_live_chunk(question: str, chunk: dict) -> bool:
    q = question.lower()
    title = str(chunk.get("title", "")).lower()
    ai_signals = ("chatbot", "ai act", "ai-wet", "kunstmatige intelligentie")
    if not any(signal in q for signal in ai_signals):
        return False
    return "arbeid" in title and "ai" not in title

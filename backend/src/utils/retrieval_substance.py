"""Retrieval substance checks — plan.md: no answer without real article text."""
from backend.src.utils.article_resolver import resolve_article_number
from backend.src.utils.legal_chunk_text import clean_chunk_text
from backend.src.utils.synthetic_chunk_detector import is_synthetic_chunk

MIN_SUBSTANTIVE_CHARS = 50


def has_substantive_retrieval(
    chunks: list[dict],
    min_chars: int = MIN_SUBSTANTIVE_CHARS,
) -> bool:
    """True when at least one chunk has a resolvable article and substantive text."""
    for chunk in chunks:
        if is_synthetic_chunk(chunk):
            continue
        article = str(chunk.get("article_number") or resolve_article_number(chunk) or "").strip()
        if not article:
            continue
        text = clean_chunk_text(str(chunk.get("text", "")))
        if len(text) >= min_chars:
            return True
    return False

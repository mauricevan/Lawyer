"""Validate cached retrieval chunks against legal source plans."""
from typing import Any

from backend.src.utils.article_chunk_filter import chunks_include_planned_articles


def cached_includes_planned_articles(
    chunks: list[dict[str, Any]],
    article_hints: tuple[str, ...] | None,
) -> bool:
    return chunks_include_planned_articles(chunks, article_hints)

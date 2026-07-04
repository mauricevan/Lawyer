"""Filter retrieval chunks to planned article numbers."""
from typing import Any


def filter_chunks_by_articles_strict(
    chunks: list[dict[str, Any]],
    article_hints: tuple[str, ...] | list[str] | None,
) -> list[dict[str, Any]]:
    if not article_hints or not chunks:
        return []
    wanted = {_normalize_article(str(article)) for article in article_hints}
    return [
        chunk for chunk in chunks
        if _normalize_article(str(chunk.get("article_number") or "")) in wanted
    ]


def filter_chunks_by_articles(
    chunks: list[dict[str, Any]],
    article_hints: tuple[str, ...] | list[str] | None,
) -> list[dict[str, Any]]:
    if not article_hints or not chunks:
        return chunks
    wanted = {_normalize_article(str(article)) for article in article_hints}
    matched = [
        chunk for chunk in chunks
        if _normalize_article(str(chunk.get("article_number") or "")) in wanted
    ]
    return matched or chunks


def chunks_include_planned_articles(
    chunks: list[dict[str, Any]],
    article_hints: tuple[str, ...] | list[str] | None,
) -> bool:
    if not article_hints or not chunks:
        return True
    wanted = {_normalize_article(str(article)) for article in article_hints}
    return any(
        _normalize_article(str(chunk.get("article_number") or "")) in wanted
        for chunk in chunks
    )


def _normalize_article(article: str) -> str:
    cleaned = article.strip().lstrip("0") or "0"
    return cleaned.split("(")[0].split(".")[0]

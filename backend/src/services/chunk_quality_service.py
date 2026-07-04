"""Detect low-quality chunks during ingest and retrieval."""
from typing import Any

from backend.src.utils.article_resolver import resolve_article_number
from backend.src.utils.legal_chunk_text import (
    clean_chunk_text,
    is_metadata_dump,
    is_recital_noise,
    matches_query_language,
)
from backend.src.utils.legal_content_quality import (
    is_usable_chunk_text,
    is_usable_legal_text,
    usable_score,
)

MIN_CHUNK_CHARS = 80


class ChunkQualityService:
    """Flags chunks that are too short, polluted, or EUR-Lex navigation HTML."""

    def is_valid(self, text: str) -> bool:
        return self.is_usable_legal_text(text)

    def is_usable_legal_text(self, text: str) -> bool:
        return is_usable_chunk_text(text)

    def usable_score(self, text: str) -> float:
        return usable_score(text)

    def filter_chunks(
        self,
        chunks: list[dict[str, Any]],
        expected_language: str | None = None,
    ) -> list[dict[str, Any]]:
        kept: list[dict[str, Any]] = []
        for chunk in chunks:
            raw = str(chunk.get("text", ""))
            text = clean_chunk_text(raw)
            if not text or not self.is_valid(text):
                continue
            if is_metadata_dump(raw) or is_recital_noise(text):
                continue
            if expected_language and not matches_query_language(text, expected_language):
                continue
            normalized = dict(chunk)
            normalized["text"] = text
            article = resolve_article_number(normalized)
            if article:
                normalized["article_number"] = article
            kept.append(normalized)
        return kept

    def summarize_batch(self, chunks: list[dict[str, Any]]) -> dict[str, int]:
        valid = self.filter_chunks(chunks)
        return {
            "total": len(chunks),
            "valid": len(valid),
            "rejected": len(chunks) - len(valid),
        }

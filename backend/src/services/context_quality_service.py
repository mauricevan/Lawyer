"""Assess whether retrieved chunks contain usable legal context for the LLM."""
from dataclasses import dataclass
from typing import Any

from backend.src.utils.classification_context_match import (
    context_supports_classification,
    is_metadata_only_context,
)
from backend.src.utils.legal_content_quality import is_usable_chunk_text, usable_score
from ingestion.src.data.cn_code_parser import is_classification_question

USABLE_SCORE_THRESHOLD = 0.35


@dataclass(frozen=True)
class ContextQualityResult:
    is_usable: bool
    reason: str | None
    best_score: float


class ContextQualityService:
    """Batch quality gate before LLM answer generation."""

    def assess(
        self,
        chunks: list[dict[str, Any]],
        question: str | None = None,
    ) -> ContextQualityResult:
        if not chunks:
            return ContextQualityResult(False, "no_chunks", 0.0)
        scores = [usable_score(str(chunk.get("text", ""))) for chunk in chunks]
        best = max(scores, default=0.0)
        if question and is_classification_question(question):
            if is_metadata_only_context(chunks) or not context_supports_classification(question, chunks):
                return ContextQualityResult(False, "classification_context_gap", best)
        substantive = [
            chunk for chunk in chunks
            if _chunk_has_substance(chunk) and not _is_navigation_chunk(chunk)
        ]
        if not substantive:
            if any(_is_navigation_chunk(chunk) for chunk in chunks):
                return ContextQualityResult(False, "all_navigation", best)
            return ContextQualityResult(False, "too_short", best)
        if question and is_metadata_only_context(chunks) and not _has_operative_chunk(substantive):
            return ContextQualityResult(False, "all_navigation", best)
        return ContextQualityResult(True, None, best)


def _chunk_has_substance(chunk: dict[str, Any]) -> bool:
    text = str(chunk.get("text", "")).strip()
    if is_metadata_only_context([chunk]):
        return False
    if not is_usable_chunk_text(text):
        return False
    score = float(chunk.get("score", 0.0) or chunk.get("rerank_score", 0.0))
    if score >= USABLE_SCORE_THRESHOLD and len(text) >= 40:
        return True
    if is_usable_chunk_text(text) and len(text) >= 120:
        return True
    if chunk.get("source") != "live_fallback" and len(text) >= 80:
        return True
    return usable_score(text) >= 0.2 and len(text) >= 100


def _has_operative_chunk(chunks: list[dict[str, Any]]) -> bool:
    joined = " ".join(str(chunk.get("text", "")) for chunk in chunks).lower()
    return any(marker in joined for marker in ("artikel", "article", "hoofdstuk", "bijlage"))


def _is_navigation_chunk(chunk: dict[str, Any]) -> bool:
    text = str(chunk.get("text", "")).lower()
    return "skip to main content" in text or "my eur-lex" in text

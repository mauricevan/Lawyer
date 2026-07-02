"""Detect low-quality chunks during ingest and retrieval."""
from typing import Any

MIN_CHUNK_CHARS = 80
DIRTY_MARKERS = ("lorem ipsum", "javascript:", "click here")


class ChunkQualityService:
    """Flags chunks that are too short or obviously polluted."""

    def is_valid(self, text: str) -> bool:
        cleaned = text.strip()
        if len(cleaned) < MIN_CHUNK_CHARS:
            return False
        lowered = cleaned.lower()
        return not any(marker in lowered for marker in DIRTY_MARKERS)

    def filter_chunks(self, chunks: list[dict[str, Any]]) -> list[dict[str, Any]]:
        return [chunk for chunk in chunks if self.is_valid(str(chunk.get("text", "")))]

    def summarize_batch(self, chunks: list[dict[str, Any]]) -> dict[str, int]:
        valid = self.filter_chunks(chunks)
        return {
            "total": len(chunks),
            "valid": len(valid),
            "rejected": len(chunks) - len(valid),
        }

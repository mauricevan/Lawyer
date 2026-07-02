"""Validate chunk and document metadata during ingest (plan7 N)."""
from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml

from shared.schemas.document import DocumentMetadata, DocumentChunk

_RULES_PATH = Path(__file__).resolve().parents[1] / "data" / "chunk_quality_rules.yaml"


@lru_cache(maxsize=1)
def _load_rules() -> dict[str, Any]:
    with open(_RULES_PATH, encoding="utf-8") as handle:
        return yaml.safe_load(handle)


class ChunkMetadataValidator:
    """Enforces chunk quality rules from chunk_quality_rules.yaml."""

    def validate_document(self, metadata: DocumentMetadata) -> list[str]:
        rules = _load_rules()
        errors: list[str] = []
        for field in rules.get("required_document_fields", []):
            if not getattr(metadata, field, None):
                errors.append(f"missing field: {field}")
        return errors

    def is_valid_chunk_text(self, text: str) -> bool:
        rules = _load_rules()
        cleaned = text.strip()
        if len(cleaned) < int(rules.get("min_chunk_chars", 80)):
            return False
        lowered = cleaned.lower()
        return not any(marker in lowered for marker in rules.get("forbidden_text_markers", []))

    def filter_valid_chunks(self, chunks: list[DocumentChunk]) -> list[DocumentChunk]:
        return [chunk for chunk in chunks if self.is_valid_chunk_text(chunk.text)]

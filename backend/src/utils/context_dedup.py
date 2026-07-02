"""Deduplicate retrieval chunks by chunk_id and text similarity."""
import hashlib
from typing import Any


def deduplicate_chunks(chunks: list[dict[str, Any]], max_chunks: int = 8) -> list[dict[str, Any]]:
    seen_ids: set[str] = set()
    seen_hashes: set[str] = set()
    output: list[dict[str, Any]] = []
    for chunk in chunks:
        chunk_id = chunk.get("chunk_id")
        if chunk_id and chunk_id in seen_ids:
            continue
        text_hash = hashlib.sha256(str(chunk.get("text", "")).encode("utf-8")).hexdigest()
        if text_hash in seen_hashes:
            continue
        if chunk_id:
            seen_ids.add(chunk_id)
        seen_hashes.add(text_hash)
        output.append(chunk)
        if len(output) >= max_chunks:
            break
    return output

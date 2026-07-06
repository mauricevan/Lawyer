"""Detect ingest fallback placeholder text — must never ground published answers."""
from typing import Any

_SYNTHETIC_MARKERS = (
    "marktdeelnemers onder",
    "kernverplichtingen. marktdeelnemers",
    "governance, transparantie, rapportage en handhaving",
    "toezichthouders controleren naleving van",
    "doel en reikwijdte. deze richtlijn (",
    "doel en reikwijdte. deze verordening (",
    "toepassingsgebied. onder ",
    "stelt regels vast voor consumer rights",
)


def is_synthetic_chunk(chunk: dict[str, Any]) -> bool:
    """True when chunk text matches fallback_subdivisions placeholder patterns."""
    text = str(chunk.get("text", "")).lower()
    if not text.strip():
        return False
    return any(marker in text for marker in _SYNTHETIC_MARKERS)


def filter_non_synthetic_chunks(chunks: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Drop synthetic placeholder chunks; keep empty list if all were synthetic."""
    return [chunk for chunk in chunks if not is_synthetic_chunk(chunk)]


def chunks_contain_only_synthetic(chunks: list[dict[str, Any]]) -> bool:
    """True when every chunk is synthetic or list is empty."""
    if not chunks:
        return True
    return all(is_synthetic_chunk(chunk) for chunk in chunks)

"""Language fallback chain for indexed retrieval (plan7 / I2)."""
from ingestion.src.data.language_registry_loader import get_fetch_fallback_chain

_CORPUS_FALLBACK = "nl"


def retrieval_language_chain(language: str | None) -> tuple[str, ...]:
    """Return languages to try in Qdrant/FTS order, ending with corpus fallback."""
    primary = (language or _CORPUS_FALLBACK).lower().split("-")[0]
    ordered = list(get_fetch_fallback_chain(primary))
    if _CORPUS_FALLBACK not in ordered:
        ordered.append(_CORPUS_FALLBACK)
    seen: set[str] = set()
    output: list[str] = []
    for code in ordered:
        if code not in seen:
            seen.add(code)
            output.append(code)
    return tuple(output)

"""Detect questions about fictional or unsupported topics."""
_FICTIONAL_TERMS = (
    "quantum teleportatie",
    "teleportatie",
    "tijdmachine",
    "parallel universum",
)


def has_unsupported_fictional_terms(question: str, chunks: list[dict]) -> bool:
    lowered = question.lower()
    corpus = " ".join(str(chunk.get("text", "")) for chunk in chunks).lower()
    for term in _FICTIONAL_TERMS:
        if term in lowered and term not in corpus:
            return True
    return False

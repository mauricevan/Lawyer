"""Check whether retrieved chunks match the user's question."""
from backend.src.services.celex_discovery_service import CelexDiscoveryService
from backend.src.services.context_quality_service import ContextQualityService
from backend.src.utils.fictional_question_guard import has_unsupported_fictional_terms
from ingestion.src.data.legal_term_hints import match_celex_hints, match_primary_celex_hint
from backend.src.utils.classification_context_match import context_supports_classification


def question_matches_chunks(
    question: str,
    chunks: list[dict],
    confirmed_celex: str | None = None,
) -> bool:
    """Return True when chunks plausibly support the question."""
    if not chunks:
        return False
    if has_unsupported_fictional_terms(question, chunks):
        return False
    discovery_celex = confirmed_celex or CelexDiscoveryService().high_confidence_celex(question)
    if discovery_celex:
        discovery_chunks = [chunk for chunk in chunks if str(chunk.get("celex", "")) == discovery_celex]
        if discovery_chunks and ContextQualityService().assess(discovery_chunks, question).is_usable:
            return True
    hints = match_celex_hints(question)
    if len(hints) >= 2:
        matched = [chunk for chunk in chunks if str(chunk.get("celex", "")) in hints]
        if matched and ContextQualityService().assess(matched, question).is_usable:
            return True
        for celex in hints:
            celex_chunks = [chunk for chunk in chunks if str(chunk.get("celex", "")) == celex]
            if celex_chunks and ContextQualityService().assess(celex_chunks, question).is_usable:
                return True
    hint = match_primary_celex_hint(question)
    if hint:
        hint_chunks = [chunk for chunk in chunks if str(chunk.get("celex", "")) == hint]
        if not hint_chunks:
            return False
        return ContextQualityService().assess(hint_chunks, question).is_usable
    hints = match_celex_hints(question)
    if hints:
        matched = [chunk for chunk in chunks if str(chunk.get("celex", "")) in hints]
        if not matched:
            return False
        return ContextQualityService().assess(matched, question).is_usable
    if not context_supports_classification(question, chunks):
        return False
    return _keyword_overlap(question, chunks)


def _keyword_overlap(question: str, chunks: list[dict]) -> bool:
    tokens = {word for word in question.lower().split() if len(word) > 4}
    if not tokens:
        return True
    corpus = " ".join(str(chunk.get("text", "")) for chunk in chunks).lower()
    hits = sum(1 for token in tokens if token in corpus)
    return hits >= min(2, len(tokens))

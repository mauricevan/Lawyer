"""Validates that answer citations match retrieval context."""
from shared.schemas.citation import Citation


class SourceConsistencyService:
    """Ensures cited CELEX values were present in retrieved chunks."""

    def find_invalid_citations(
        self,
        citations: list[Citation],
        context_chunks: list[dict],
    ) -> list[str]:
        allowed = {chunk.get("celex") for chunk in context_chunks if chunk.get("celex")}
        if not allowed:
            return []
        invalid: list[str] = []
        for citation in citations:
            if citation.celex and citation.celex not in allowed:
                invalid.append(citation.celex)
        return invalid

    def filter_citations(
        self,
        citations: list[Citation],
        context_chunks: list[dict],
    ) -> list[Citation]:
        allowed = {chunk.get("celex") for chunk in context_chunks if chunk.get("celex")}
        if not allowed:
            return citations
        return [citation for citation in citations if citation.celex in allowed]

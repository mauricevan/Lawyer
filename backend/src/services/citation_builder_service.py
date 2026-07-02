"""Build structured citations from retrieval chunks."""
from shared.schemas.citation import Citation


class CitationBuilderService:
    """Creates citation objects from ranked retrieval chunks."""

    def from_chunks(self, chunks: list[dict], limit: int = 8) -> list[Citation]:
        seen: set[tuple[str | None, str | None]] = set()
        citations: list[Citation] = []
        for chunk in chunks:
            key = (chunk.get("celex"), chunk.get("article_number"))
            if key in seen:
                continue
            seen.add(key)
            celex = chunk.get("celex", "")
            citations.append(Citation(
                celex=celex,
                article=str(chunk.get("article_number")) if chunk.get("article_number") else None,
                title=chunk.get("title"),
                excerpt=chunk.get("text", "")[:400],
                eli_uri=chunk.get("eli_uri"),
                eurlex_url=f"https://eur-lex.europa.eu/legal-content/NL/TXT/?uri=CELEX:{celex}",
            ))
            if len(citations) >= limit:
                break
        return citations

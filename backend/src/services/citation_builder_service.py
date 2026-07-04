"""Build structured citations from retrieval chunks."""
from backend.src.utils.article_resolver import resolve_article_number
from shared.schemas.citation import Citation


class CitationBuilderService:
    """Creates citation objects from ranked retrieval chunks."""

    def from_chunks(self, chunks: list[dict], limit: int = 8) -> list[Citation]:
        seen: set[tuple[str | None, str | None]] = set()
        citations: list[Citation] = []
        for chunk in chunks:
            article = resolve_article_number(chunk)
            key = (chunk.get("celex"), article)
            if key in seen:
                continue
            seen.add(key)
            celex = chunk.get("celex", "")
            citations.append(Citation(
                celex=celex,
                article=article,
                title=chunk.get("title"),
                excerpt=chunk.get("text", "")[:400],
                eli_uri=chunk.get("eli_uri"),
                eurlex_url=f"https://eur-lex.europa.eu/legal-content/NL/TXT/?uri=CELEX:{celex}",
            ))
            if len(citations) >= limit:
                break
        return citations

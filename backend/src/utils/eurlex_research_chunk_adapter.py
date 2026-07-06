"""Map in-document research hits to agent retrieval chunks."""
from backend.src.utils.in_document_search import ArticleSearchHit


def hits_to_retrieval_chunks(hits: list[ArticleSearchHit]) -> list[dict]:
    """Convert live article hits into AgentFetchResult chunk dicts."""
    chunks: list[dict] = []
    for hit in hits:
        chunks.append(
            {
                "chunk_id": f"research:{hit.celex}:{hit.article_number}",
                "celex": hit.celex,
                "title": hit.title,
                "text": hit.text,
                "article_number": hit.article_number,
                "language": "nl",
                "is_consolidated": True,
                "is_in_force": True,
                "eli_uri": None,
                "score": hit.score,
                "source": "eurlex_research",
                "matched_terms": list(hit.matched_terms),
            },
        )
    return chunks

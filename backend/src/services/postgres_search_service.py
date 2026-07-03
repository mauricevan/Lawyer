"""PostgreSQL full-text search over indexed chunk text."""
import logging
from typing import Any

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from ingestion.src.data.language_registry_loader import get_fts_config

logger = logging.getLogger(__name__)


class PostgresSearchService:
    """Runs language-aware FTS queries against chunk search vectors."""

    async def search(
        self,
        session: AsyncSession,
        query: str,
        language: str | None = None,
        limit: int = 50,
        excluded_celex: set[str] | None = None,
    ) -> list[dict[str, Any]]:
        cleaned = query.strip()
        if len(cleaned) < 3:
            return []
        config = get_fts_config(language or "nl")
        excluded = sorted(excluded_celex or [])
        exclusion_clause = ""
        params: dict[str, Any] = {"config": config, "query": cleaned, "limit": limit}
        if excluded:
            exclusion_clause = "AND c.celex NOT IN :excluded_celex"
            params["excluded_celex"] = tuple(excluded)
        try:
            async with session.begin_nested():
                result = await session.execute(
                    text(
                        f"""
                        SELECT c.chunk_id, c.celex, c.article_ref, d.title, d.language,
                               ts_rank(c.search_vector, plainto_tsquery(:config, :query)) AS rank
                        FROM chunks c
                        JOIN documents d ON d.id = c.document_id
                        WHERE c.search_vector @@ plainto_tsquery(:config, :query)
                        {exclusion_clause}
                        ORDER BY rank DESC
                        LIMIT :limit
                        """
                    ),
                    params,
                )
        except Exception as exc:
            logger.warning("PostgreSQL FTS search failed: %s", exc)
            return []
        rows = result.mappings().all()
        return [
            {
                "chunk_id": row["chunk_id"],
                "celex": row["celex"],
                "title": row["title"],
                "text": "",
                "article_number": row["article_ref"],
                "language": row["language"],
                "score": float(row["rank"] or 0.0),
                "fts_score": float(row["rank"] or 0.0),
                "source": "postgres_fts",
            }
            for row in rows
        ]

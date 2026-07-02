"""PostgreSQL full-text search over indexed chunk text."""
import logging
from typing import Any

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)

TS_CONFIG = {"nl": "dutch", "en": "english"}


class PostgresSearchService:
    """Runs language-aware FTS queries against chunk search vectors."""

    async def search(
        self,
        session: AsyncSession,
        query: str,
        language: str | None = None,
        limit: int = 50,
    ) -> list[dict[str, Any]]:
        cleaned = query.strip()
        if len(cleaned) < 3:
            return []
        config = TS_CONFIG.get((language or "nl").lower(), "simple")
        try:
            async with session.begin_nested():
                result = await session.execute(
                    text(
                        """
                        SELECT c.chunk_id, c.celex, c.article_ref, d.title, d.language,
                               ts_rank(c.search_vector, plainto_tsquery(:config, :query)) AS rank
                        FROM chunks c
                        JOIN documents d ON d.id = c.document_id
                        WHERE c.search_vector @@ plainto_tsquery(:config, :query)
                        ORDER BY rank DESC
                        LIMIT :limit
                        """
                    ),
                    {"config": config, "query": cleaned, "limit": limit},
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

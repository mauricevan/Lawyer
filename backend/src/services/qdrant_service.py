"""Qdrant vector store operations with hybrid search support."""
import logging
import uuid
from typing import Any

from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    FieldCondition,
    Filter,
    HnswConfigDiff,
    MatchValue,
    PayloadSchemaType,
    PointStruct,
    VectorParams,
)

from backend.src.config import settings
from backend.src.services.embedding_service import EMBEDDING_DIM
from backend.src.utils.qdrant_filters import build_qdrant_filter
from backend.src.utils.retrieval_language_chain import retrieval_language_chain
from shared.schemas.document import DocumentChunk
from shared.schemas.query import QueryFilters

logger = logging.getLogger(__name__)


class QdrantService:
    """Manages chunk vectors in Qdrant."""

    def __init__(self) -> None:
        self._client = QdrantClient(
            url=settings.qdrant_url,
            check_compatibility=False,
        )
        self._collection = settings.qdrant_collection

    def ensure_collection(self) -> None:
        collections = [c.name for c in self._client.get_collections().collections]
        if self._collection not in collections:
            self._client.create_collection(
                collection_name=self._collection,
                vectors_config=VectorParams(size=EMBEDDING_DIM, distance=Distance.COSINE),
                hnsw_config=HnswConfigDiff(
                    m=settings.qdrant_hnsw_m,
                    ef_construct=settings.qdrant_hnsw_ef_construct,
                ),
            )
            logger.info("Created Qdrant collection: %s", self._collection)
        self._ensure_payload_indexes()

    def _ensure_payload_indexes(self) -> None:
        for field_name, schema in (
            ("celex", PayloadSchemaType.KEYWORD),
            ("language", PayloadSchemaType.KEYWORD),
            ("is_in_force", PayloadSchemaType.BOOL),
        ):
            try:
                self._client.create_payload_index(
                    collection_name=self._collection,
                    field_name=field_name,
                    field_schema=schema,
                )
            except Exception:
                pass

    def upsert_chunks(
        self, chunks: list[DocumentChunk], vectors: list[list[float]]
    ) -> None:
        self.ensure_collection()
        points = []
        for chunk, vector in zip(chunks, vectors):
            point_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, chunk.chunk_id))
            payload = {
                "chunk_id": chunk.chunk_id,
                "celex": chunk.celex,
                "text": chunk.text,
                "article_number": chunk.article_number,
                "subdivision_type": chunk.subdivision_type,
                "language": chunk.language,
                "is_consolidated": chunk.is_consolidated,
                "is_in_force": chunk.is_in_force,
                "title": chunk.title,
                "oj_reference": chunk.oj_reference,
                "eli_uri": chunk.eli_uri,
                "version_type": chunk.version_type.value if hasattr(chunk.version_type, "value") else str(chunk.version_type),
            }
            points.append(PointStruct(id=point_id, vector=vector, payload=payload))
        self._client.upsert(collection_name=self._collection, points=points)

    def search(
        self,
        query_vector: list[float],
        limit: int = 50,
        language: str | None = None,
        in_force_only: bool = True,
        filters: QueryFilters | None = None,
    ) -> list[dict[str, Any]]:
        self.ensure_collection()
        query_filter = build_qdrant_filter(filters, language, in_force_only)
        response = self._client.query_points(
            collection_name=self._collection,
            query=query_vector,
            limit=limit,
            query_filter=query_filter,
            with_payload=True,
        )
        return [
            {"score": point.score, **(point.payload or {})}
            for point in response.points
        ]

    def search_with_language_fallback(
        self,
        query_vector: list[float],
        limit: int = 50,
        language: str | None = None,
        in_force_only: bool = True,
        filters: QueryFilters | None = None,
        min_results: int = 1,
    ) -> list[dict[str, Any]]:
        """Search Qdrant, trying registry fallback chain plus corpus language."""
        for lang in retrieval_language_chain(language):
            attempt_filters = self._filters_for_language(filters, lang)
            results = self.search(
                query_vector,
                limit=limit,
                language=lang,
                in_force_only=in_force_only,
                filters=attempt_filters,
            )
            if len(results) >= min_results:
                return results
        return []

    def search_by_celex_with_language_fallback(
        self,
        celex_values: set[str],
        limit: int = 12,
        language: str | None = "nl",
        in_force_only: bool = True,
    ) -> list[dict[str, Any]]:
        """Fetch CELEX chunks, falling back across language chain."""
        for lang in retrieval_language_chain(language):
            results = self.search_by_celex(
                celex_values=celex_values,
                limit=limit,
                language=lang,
                in_force_only=in_force_only,
            )
            if results:
                return results
        return []

    @staticmethod
    def _filters_for_language(
        filters: QueryFilters | None,
        language: str,
    ) -> QueryFilters | None:
        if not filters:
            return None
        return filters.model_copy(update={"language": language})

    def search_by_celex(
        self,
        celex_values: set[str],
        limit: int = 12,
        language: str | None = "nl",
        in_force_only: bool = True,
    ) -> list[dict[str, Any]]:
        """Fetch chunks directly by CELEX for lexical fallback cases."""
        if not celex_values:
            return []
        self.ensure_collection()
        celex_conditions = [
            FieldCondition(key="celex", match=MatchValue(value=celex))
            for celex in celex_values
        ]
        must_conditions: list[FieldCondition] = []
        if language:
            must_conditions.append(
                FieldCondition(key="language", match=MatchValue(value=language))
            )
        if in_force_only:
            must_conditions.append(
                FieldCondition(key="is_in_force", match=MatchValue(value=True))
            )
        query_filter = Filter(must=must_conditions, should=celex_conditions)
        points, _ = self._client.scroll(
            collection_name=self._collection,
            scroll_filter=query_filter,
            limit=limit,
            with_payload=True,
            with_vectors=False,
        )
        return [{"score": 1.0, **(point.payload or {})} for point in points]

    def count_points(self) -> int:
        try:
            info = self._client.get_collection(self._collection)
            return info.points_count or 0
        except Exception:
            return 0

    def delete_by_celex(self, celex: str) -> None:
        """Remove all vector points for a CELEX identifier."""
        try:
            self._client.delete(
                collection_name=self._collection,
                points_selector=Filter(
                    must=[FieldCondition(key="celex", match=MatchValue(value=celex))]
                ),
            )
        except Exception as exc:
            logger.warning("Qdrant delete failed for %s: %s", celex, exc)

    def delete_by_chunk_id(self, chunk_id: str) -> None:
        """Remove a single vector point by chunk_id payload key."""
        try:
            point_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, chunk_id))
            self._client.delete(
                collection_name=self._collection,
                points_selector=[point_id],
            )
        except Exception as exc:
            logger.warning("Qdrant delete failed for chunk %s: %s", chunk_id, exc)

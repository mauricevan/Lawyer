"""Index a single document into PostgreSQL and Qdrant."""
import asyncio
import logging
import uuid
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from backend.src.config import settings
from backend.src.database import Base
from backend.src.models.tables import Chunk, Document
from backend.src.services.embedding_service import get_embedding_service
from backend.src.services.qdrant_service import QdrantService
from ingestion.src.chunkers.legal_chunker import LegalChunker
from ingestion.src.clients.cellar_rest_client import CellarRestClient
from ingestion.src.content.fallback_subdivisions import build_fallback_subdivisions, needs_fallback
from ingestion.src.data.sample_articles import SAMPLE_ARTICLES
from ingestion.src.parsers.document_parser import DocumentParser
from ingestion.src.validators.chunk_metadata_validator import ChunkMetadataValidator
from shared.schemas.document import DocumentMetadata

logger = logging.getLogger(__name__)

UPSERT_BATCH_SIZE = 64


async def ingest_document(
    metadata: DocumentMetadata,
    session: AsyncSession,
    use_live_fetch: bool = True,
    cellar: CellarRestClient | None = None,
) -> int:
    """Fetch, parse, chunk, embed and store one document. Returns chunk count."""
    validator = ChunkMetadataValidator()
    doc_errors = validator.validate_document(metadata)
    if doc_errors:
        logger.warning("Invalid metadata for %s: %s", metadata.celex, doc_errors)
        return 0
    parser = DocumentParser()
    chunker = LegalChunker()
    client = cellar or CellarRestClient()
    subdivisions = await _fetch_subdivisions(metadata, parser, client, use_live_fetch)
    if needs_fallback(subdivisions):
        subdivisions = build_fallback_subdivisions(metadata)
    if not subdivisions:
        logger.warning("No content for %s", metadata.celex)
        return 0
    doc = await _upsert_document(metadata, session)
    chunks = validator.filter_valid_chunks(chunker.chunk_document(subdivisions, metadata))
    if not chunks:
        logger.warning("No valid chunks for %s after quality filter", metadata.celex)
        return 0
    embeddings = get_embedding_service()
    qdrant = QdrantService()
    for start in range(0, len(chunks), UPSERT_BATCH_SIZE):
        batch = chunks[start : start + UPSERT_BATCH_SIZE]
        vectors = embeddings.embed_passages([c.text for c in batch])
        qdrant.upsert_chunks(batch, vectors)
    for chunk in chunks:
        await _upsert_chunk(chunk, doc.id, session)
    doc.indexed_at = datetime.now(timezone.utc)
    await session.commit()
    logger.info("Indexed %s: %d chunks", metadata.celex, len(chunks))
    return len(chunks)


async def _fetch_subdivisions(
    metadata: DocumentMetadata,
    parser: DocumentParser,
    cellar: CellarRestClient,
    use_live_fetch: bool,
) -> list[dict]:
    if metadata.celex in SAMPLE_ARTICLES:
        samples = SAMPLE_ARTICLES[metadata.celex]
        return [{"title": metadata.title, "celex": metadata.celex, **s} for s in samples]
    if not use_live_fetch:
        return []
    try:
        content = await cellar.fetch_by_celex(metadata.celex, metadata.language)
        content_type = "xml" if content[:5] == b"<?xml" else "html"
        return parser.parse(content, metadata.celex, content_type)
    except Exception as exc:
        logger.warning("Live fetch failed for %s: %s", metadata.celex, exc)
        return []


async def _upsert_document(metadata: DocumentMetadata, session: AsyncSession) -> Document:
    result = await session.execute(
        select(Document).where(
            Document.celex == metadata.celex,
            Document.language == metadata.language,
        )
    )
    existing = result.scalar_one_or_none()
    if existing:
        return existing
    doc = Document(
        celex=metadata.celex,
        cellar_id=metadata.cellar_id,
        eli_uri=metadata.eli_uri,
        doc_type=metadata.doc_type,
        language=metadata.language,
        title=metadata.title,
        short_title=metadata.short_title,
        is_in_force=metadata.is_in_force,
        is_consolidated=metadata.is_consolidated,
        version_type=metadata.version_type.value,
        oj_reference=metadata.oj_reference,
        corrigendum_celex=metadata.corrigendum_celex,
    )
    session.add(doc)
    await session.flush()
    return doc


async def _upsert_chunk(chunk, document_id: uuid.UUID, session: AsyncSession) -> None:
    result = await session.execute(select(Chunk).where(Chunk.chunk_id == chunk.chunk_id))
    if result.scalar_one_or_none():
        return
    session.add(Chunk(
        chunk_id=chunk.chunk_id,
        document_id=document_id,
        celex=chunk.celex,
        article_ref=chunk.article_number,
        text=chunk.text[:8000],
        text_hash=chunk.text_hash,
    ))

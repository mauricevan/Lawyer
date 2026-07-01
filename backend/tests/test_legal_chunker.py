"""Unit tests for legal chunker."""
from ingestion.src.chunkers.legal_chunker import LegalChunker
from shared.schemas.document import DocumentMetadata, VersionType


def test_chunk_document_creates_chunks_with_celex_prefix() -> None:
    chunker = LegalChunker()
    meta = DocumentMetadata(
        celex="32024R1689",
        cellar_id=None,
        title="AI Act",
        version_type=VersionType.CONSOLIDATED,
        is_consolidated=True,
    )
    subs = [{
        "article_number": "5",
        "subdivision_type": "article",
        "text": "Artikel 5 Verboden AI-praktijken. " * 50,
    }]
    chunks = chunker.chunk_document(subs, meta)
    assert len(chunks) >= 1
    assert "32024R1689" in chunks[0].text
    assert chunks[0].article_number == "5"


def test_chunk_short_article_single_chunk() -> None:
    chunker = LegalChunker()
    meta = DocumentMetadata(celex="32016R0679", cellar_id=None, title="GDPR")
    subs = [{"article_number": "6", "subdivision_type": "article", "text": "Korte tekst artikel 6."}]
    chunks = chunker.chunk_document(subs, meta)
    assert len(chunks) == 1

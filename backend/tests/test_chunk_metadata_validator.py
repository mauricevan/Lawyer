"""Tests for chunk metadata validator (plan7 N)."""
from ingestion.src.validators.chunk_metadata_validator import ChunkMetadataValidator
from shared.schemas.document import DocumentChunk, DocumentMetadata, VersionType


def _metadata(**overrides) -> DocumentMetadata:
    base = {
        "celex": "32016R0679",
        "cellar_id": "cellar-1",
        "eli_uri": "http://example.com",
        "doc_type": "regulation",
        "language": "nl",
        "title": "GDPR",
        "short_title": "GDPR",
        "is_in_force": True,
        "is_consolidated": True,
        "version_type": VersionType.CONSOLIDATED,
    }
    base.update(overrides)
    return DocumentMetadata(**base)


def test_validate_document_requires_celex() -> None:
    validator = ChunkMetadataValidator()
    errors = validator.validate_document(_metadata(celex=""))
    assert any("celex" in error for error in errors)


def test_filter_rejects_short_chunks() -> None:
    validator = ChunkMetadataValidator()
    chunks = [
        DocumentChunk(
            chunk_id="c1",
            celex="32016R0679",
            article_number="1",
            text="too short",
            text_hash="abc",
        )
    ]
    assert validator.filter_valid_chunks(chunks) == []


def test_filter_rejects_forbidden_markers() -> None:
    validator = ChunkMetadataValidator()
    chunks = [
        DocumentChunk(
            chunk_id="c2",
            celex="32016R0679",
            article_number="2",
            text="x" * 100 + " lorem ipsum " + "y" * 10,
            text_hash="def",
        )
    ]
    assert validator.filter_valid_chunks(chunks) == []

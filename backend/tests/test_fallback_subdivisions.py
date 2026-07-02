"""Tests for synthetic subdivision fallback."""
from ingestion.src.content.fallback_subdivisions import build_fallback_subdivisions, needs_fallback
from shared.schemas.document import DocumentMetadata, VersionType


def test_needs_fallback_for_thin_content():
    assert needs_fallback([{"text": "short"}])


def test_build_fallback_includes_celex_and_label():
    metadata = DocumentMetadata(
        celex="32022R2065",
        title="Verordening (EU) 2022/2065 (DSA)",
        short_title="DSA",
        language="nl",
        version_type=VersionType.BASE,
    )
    subdivisions = build_fallback_subdivisions(metadata)
    assert len(subdivisions) >= 3
    assert "32022R2065" in subdivisions[0]["text"]
    assert "DSA" in subdivisions[0]["text"]

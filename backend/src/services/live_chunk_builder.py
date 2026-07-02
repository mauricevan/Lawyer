"""Live fallback chunk builder using ingestion parse/chunk pipeline."""
from typing import Any

from ingestion.src.chunkers.legal_chunker import LegalChunker
from ingestion.src.parsers.document_parser import DocumentParser
from shared.schemas.document import DocumentMetadata, VersionType


class LiveChunkBuilder:
    """Builds retrieval chunks from raw EUR-Lex HTML."""

    def __init__(self) -> None:
        self._parser = DocumentParser()
        self._chunker = LegalChunker()

    def build_from_html(
        self,
        celex: str,
        html: bytes,
        language: str,
        title: str,
        metadata: dict[str, str] | None,
    ) -> list[dict[str, Any]]:
        subdivisions = self._parser.parse(html, celex, "html")
        if not subdivisions:
            return []
        doc_meta = DocumentMetadata(
            celex=celex,
            title=title or f"EUR-Lex CELEX {celex}",
            language=language,
            version_type=VersionType.BASE,
        )
        chunks = self._chunker.chunk_document(subdivisions, doc_meta)[:3]
        return [self._to_retrieval_dict(chunk, metadata) for chunk in chunks]

    def _to_retrieval_dict(self, chunk, metadata: dict[str, str] | None) -> dict[str, Any]:
        return {
            "chunk_id": f"live:{chunk.chunk_id}",
            "celex": chunk.celex,
            "title": chunk.title,
            "text": chunk.text,
            "article_number": chunk.article_number,
            "language": chunk.language,
            "is_consolidated": chunk.is_consolidated,
            "is_in_force": chunk.is_in_force,
            "eli_uri": chunk.eli_uri or (metadata.get("modified") if metadata else None),
            "score": 1.0,
            "source": "live_fallback",
        }

"""Legal text chunker — splits subdivisions into searchable chunks."""
import hashlib
import uuid
from typing import Any

import tiktoken

from shared.schemas.document import DocumentChunk, DocumentMetadata, VersionType

MAX_TOKENS = 512
OVERLAP_TOKENS = 64


class LegalChunker:
    """Chunks legal subdivisions with CELEX/article metadata prefixes."""

    def __init__(self) -> None:
        self._enc = tiktoken.get_encoding("cl100k_base")

    def chunk_document(
        self,
        subdivisions: list[dict[str, Any]],
        metadata: DocumentMetadata,
    ) -> list[DocumentChunk]:
        chunks: list[DocumentChunk] = []
        for sub in subdivisions:
            text = sub.get("text", "")
            article = sub.get("article_number")
            sub_type = sub.get("subdivision_type", "article")
            token_chunks = self._split_tokens(text)
            for i, token_text in enumerate(token_chunks):
                prefix = self._build_prefix(metadata, article, sub_type)
                full_text = f"{prefix}\n{token_text}"
                chunk_id = f"{metadata.celex}_{article or 'body'}_{i}"
                chunks.append(DocumentChunk(
                    chunk_id=chunk_id,
                    celex=metadata.celex,
                    text=full_text,
                    article_number=str(article) if article else None,
                    subdivision_type=sub_type,
                    language=metadata.language,
                    version_type=metadata.version_type,
                    is_consolidated=metadata.is_consolidated,
                    is_in_force=metadata.is_in_force,
                    eli_uri=metadata.eli_uri,
                    title=metadata.title,
                    oj_reference=metadata.oj_reference,
                    text_hash=self._hash(full_text),
                ))
        return chunks

    def _build_prefix(
        self, meta: DocumentMetadata, article: str | None, sub_type: str
    ) -> str:
        parts = [f"CELEX:{meta.celex}", meta.title]
        if article:
            parts.append(f"Artikel {article}")
        parts.append(sub_type)
        return " | ".join(parts)

    def _split_tokens(self, text: str) -> list[str]:
        tokens = self._enc.encode(text)
        if len(tokens) <= MAX_TOKENS:
            return [text]
        chunks = []
        start = 0
        while start < len(tokens):
            end = min(start + MAX_TOKENS, len(tokens))
            chunks.append(self._enc.decode(tokens[start:end]))
            if end >= len(tokens):
                break
            start = end - OVERLAP_TOKENS
        return chunks

    @staticmethod
    def _hash(text: str) -> str:
        return hashlib.sha256(text.encode()).hexdigest()[:16]

"""Live fallback chunk builder using ingestion parse/chunk pipeline."""
from typing import Any

from backend.src.utils.article_resolver import resolve_article_number

from ingestion.src.chunkers.legal_chunker import LegalChunker
from ingestion.src.data.cn_code_parser import (
    extract_cn_code,
    extract_cn_code_full,
    is_classification_question,
)
from ingestion.src.parsers.document_parser import DocumentParser
from shared.schemas.document import DocumentMetadata, VersionType

DEFAULT_CHUNK_LIMIT = 3
DOMAIN_CHUNK_LIMIT = 8
CLASSIFICATION_CHUNK_LIMIT = 10
PLANNED_ARTICLE_LIMIT = 8
AGENT_ARTICLE_LIMIT = 12


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
        question: str | None = None,
        article_hints: tuple[str, ...] | None = None,
        strict_articles: bool = False,
        search_keywords: tuple[str, ...] | None = None,
        agent_mode: bool = False,
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
        chunks = self._chunker.chunk_document(subdivisions, doc_meta)
        if article_hints:
            filtered = self._filter_by_articles(chunks, article_hints)
            if strict_articles:
                if not filtered:
                    return []
                chunks = filtered
            else:
                chunks = filtered if filtered else chunks
        elif search_keywords:
            chunks = self._rank_by_keywords(chunks, search_keywords)
        if question and is_classification_question(question):
            chunks = self._rank_classification_chunks(chunks, question)[:CLASSIFICATION_CHUNK_LIMIT]
        elif article_hints or agent_mode:
            limit = AGENT_ARTICLE_LIMIT if agent_mode else PLANNED_ARTICLE_LIMIT
            chunks = chunks[:limit]
        else:
            chunks = chunks[:DOMAIN_CHUNK_LIMIT]
        return [self._to_retrieval_dict(chunk, metadata) for chunk in chunks]

    @staticmethod
    def _filter_by_articles(chunks: list, article_hints: tuple[str, ...]) -> list:
        wanted = {hint.lstrip("0") or "0" for hint in article_hints}
        matched = []
        for chunk in chunks:
            article = LiveChunkBuilder._chunk_article(chunk)
            if article and article.lstrip("0") in wanted:
                matched.append(chunk)
        return matched

    @staticmethod
    def _chunk_article(chunk) -> str | None:
        if chunk.article_number:
            return str(chunk.article_number)
        return resolve_article_number({"text": chunk.text})

    def _rank_by_keywords(self, chunks: list, keywords: tuple[str, ...]) -> list:
        lowered = [k.lower() for k in keywords if k]

        def score(chunk) -> int:
            text = chunk.text.lower()
            return sum(2 if len(k) > 6 else 1 for k in lowered if k in text)

        ranked = sorted(chunks, key=score, reverse=True)
        return [c for c in ranked if score(c) > 0] or ranked[:AGENT_ARTICLE_LIMIT]

    def _rank_classification_chunks(self, chunks: list, question: str) -> list:
        cn_code = extract_cn_code(question) or ""
        cn_full = extract_cn_code_full(question) or ""
        lowered_question = question.lower()

        def rank(chunk) -> int:
            text = chunk.text.lower()
            compact = text.replace(" ", "").replace(".", "")
            score = 0
            if cn_code and cn_code in text:
                score += 10
            if cn_full and cn_full in compact:
                score += 20
            if "paard" in lowered_question and "paard" in text:
                score += 5
            return score

        return sorted(chunks, key=rank, reverse=True)

    def _to_retrieval_dict(self, chunk, metadata: dict[str, str] | None) -> dict[str, Any]:
        article = self._chunk_article(chunk)
        return {
            "chunk_id": f"live:{chunk.chunk_id}",
            "celex": chunk.celex,
            "title": chunk.title,
            "text": chunk.text,
            "article_number": article,
            "language": chunk.language,
            "is_consolidated": chunk.is_consolidated,
            "is_in_force": chunk.is_in_force,
            "eli_uri": chunk.eli_uri or (metadata.get("modified") if metadata else None),
            "score": 1.0,
            "source": "live_fallback",
        }

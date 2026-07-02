"""Lexical BM25 scoring over in-memory candidate chunks."""
import math
import re
from typing import Any

TOKEN_PATTERN = re.compile(r"[A-Za-zÀ-ÿ0-9]{3,}")


class Bm25Service:
    """Scores retrieval candidates with a lightweight BM25 implementation."""

    def rank(self, query: str, candidates: list[dict[str, Any]], top_k: int = 50) -> list[dict[str, Any]]:
        if not query.strip() or not candidates:
            return []
        query_terms = self._tokenize(query)
        if not query_terms:
            return []

        doc_terms = [self._tokenize(self._doc_text(candidate)) for candidate in candidates]
        avg_len = sum(len(terms) for terms in doc_terms) / max(len(doc_terms), 1)
        idf = self._inverse_doc_frequency(query_terms, doc_terms)

        scored: list[tuple[float, dict[str, Any]]] = []
        for candidate, terms in zip(candidates, doc_terms):
            score = self._bm25_score(query_terms, terms, idf, avg_len)
            if score > 0:
                scored.append((score, {**candidate, "bm25_score": score}))
        scored.sort(key=lambda item: item[0], reverse=True)
        return [item[1] for item in scored[:top_k]]

    def _doc_text(self, candidate: dict[str, Any]) -> str:
        return " ".join(
            str(candidate.get(key, ""))
            for key in ("title", "text", "celex", "article_number")
        )

    def _tokenize(self, text: str) -> list[str]:
        return [token.lower() for token in TOKEN_PATTERN.findall(text)]

    def _inverse_doc_frequency(
        self,
        query_terms: list[str],
        doc_terms: list[list[str]],
    ) -> dict[str, float]:
        doc_count = len(doc_terms)
        idf: dict[str, float] = {}
        for term in set(query_terms):
            df = sum(1 for terms in doc_terms if term in terms)
            idf[term] = math.log(1 + (doc_count - df + 0.5) / (df + 0.5))
        return idf

    def _bm25_score(
        self,
        query_terms: list[str],
        doc_terms: list[str],
        idf: dict[str, float],
        avg_len: float,
    ) -> float:
        k1 = 1.5
        b = 0.75
        doc_len = len(doc_terms) or 1
        term_freq: dict[str, int] = {}
        for term in doc_terms:
            term_freq[term] = term_freq.get(term, 0) + 1

        score = 0.0
        for term in set(query_terms):
            freq = term_freq.get(term, 0)
            if freq == 0:
                continue
            numerator = freq * (k1 + 1)
            denominator = freq + k1 * (1 - b + b * (doc_len / avg_len))
            score += idf.get(term, 0.0) * (numerator / denominator)
        return score

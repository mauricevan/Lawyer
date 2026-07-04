"""CELEX discovery from question text via title index and SPARQL."""
import json
import logging
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Literal

from backend.src.utils.celex_title_normalize import (
    score_title_overlap,
    tokenize_meaningful,
)
from ingestion.src.data.curated_loader import load_curated_documents
from ingestion.src.data.legal_term_hints import build_legal_term_celex_hints

logger = logging.getLogger(__name__)

_REPO_ROOT = Path(__file__).resolve().parents[3]
_TITLE_INDEX_PATH = _REPO_ROOT / "ingestion/data/celex_title_index.json"
_HIGH_CONFIDENCE_SCORE = 0.75
DiscoverySource = Literal["title_index", "sparql", "hint"]


@dataclass(frozen=True)
class CelexCandidate:
    celex: str
    score: float
    source: DiscoverySource
    title: str | None = None


class CelexDiscoveryService:
    """Discover CELEX candidates before hybrid retrieval."""

    def discover_sync(self, question: str, limit: int = 5) -> list[CelexCandidate]:
        """Synchronous discovery from local title index and term hints."""
        query_tokens = tokenize_meaningful(question)
        if not query_tokens:
            return []
        ranked: dict[str, CelexCandidate] = {}
        for entry in _load_title_entries():
            score = score_title_overlap(query_tokens, entry["title"])
            for alias in entry.get("aliases", []):
                score = max(score, score_title_overlap(query_tokens, alias))
            if score < 0.35:
                continue
            self._upsert(ranked, entry["celex"], score, "title_index", entry["title"])
        for hint, celex in build_legal_term_celex_hints().items():
            if hint in question.lower():
                weight = min(1.0, 0.55 + len(hint) / 80)
                self._upsert(ranked, celex, weight, "hint", hint)
        return sorted(ranked.values(), key=lambda item: item.score, reverse=True)[:limit]

    async def discover(
        self,
        question: str,
        language: str = "nl",
        limit: int = 5,
    ) -> list[CelexCandidate]:
        """Full discovery: local index first, then SPARQL ranked candidates."""
        local = self.discover_sync(question, limit=limit)
        if local and local[0].score >= _HIGH_CONFIDENCE_SCORE:
            return local
        sparql_hits = await self._discover_sparql(question, language, limit=limit)
        merged: dict[str, CelexCandidate] = {item.celex: item for item in local}
        for hit in sparql_hits:
            self._upsert(merged, hit.celex, hit.score, hit.source, hit.title)
        return sorted(merged.values(), key=lambda item: item.score, reverse=True)[:limit]

    def top_celex(self, question: str, min_score: float = 0.5) -> CelexCandidate | None:
        hits = self.discover_sync(question, limit=1)
        if hits and hits[0].score >= min_score:
            return hits[0]
        return None

    def high_confidence_celex(self, question: str) -> str | None:
        candidate = self.top_celex(question, min_score=_HIGH_CONFIDENCE_SCORE)
        return candidate.celex if candidate else None

    async def _discover_sparql(
        self,
        question: str,
        language: str,
        limit: int,
    ) -> list[CelexCandidate]:
        try:
            from ingestion.src.clients.sparql_client import SparqlClient

            rows = await SparqlClient().discover_celex_candidates(question, language, limit=limit)
            return [
                CelexCandidate(
                    celex=row["celex"],
                    score=float(row.get("score", 0.5)),
                    source="sparql",
                    title=row.get("title"),
                )
                for row in rows
                if row.get("celex")
            ]
        except Exception as exc:
            logger.warning("SPARQL CELEX discovery failed: %s", exc)
            return []

    def _upsert(
        self,
        ranked: dict[str, CelexCandidate],
        celex: str,
        score: float,
        source: DiscoverySource,
        title: str | None,
    ) -> None:
        existing = ranked.get(celex)
        if existing is None or score > existing.score:
            ranked[celex] = CelexCandidate(celex=celex, score=score, source=source, title=title)


@lru_cache(maxsize=1)
def _load_title_entries() -> list[dict[str, str | list[str]]]:
    entries: list[dict[str, str | list[str]]] = []
    seen: set[str] = set()
    for document in load_curated_documents():
        if document.celex in seen:
            continue
        seen.add(document.celex)
        aliases: list[str] = []
        if document.short_title:
            aliases.append(document.short_title)
        entries.append({"celex": document.celex, "title": document.title, "aliases": aliases})
    if _TITLE_INDEX_PATH.is_file():
        try:
            payload = json.loads(_TITLE_INDEX_PATH.read_text(encoding="utf-8"))
            for item in payload.get("entries", []):
                celex = str(item.get("celex", ""))
                if not celex or celex in seen:
                    continue
                seen.add(celex)
                entries.append({
                    "celex": celex,
                    "title": str(item.get("title", "")),
                    "aliases": list(item.get("aliases", [])),
                })
        except (json.JSONDecodeError, OSError) as exc:
            logger.warning("Failed to load CELEX title index: %s", exc)
    return entries

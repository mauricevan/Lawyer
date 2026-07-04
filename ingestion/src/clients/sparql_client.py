"""CELLAR SPARQL endpoint client with pagination."""
import asyncio
import logging
import re
from typing import Any
from urllib.parse import urlencode

import httpx

logger = logging.getLogger(__name__)

from ingestion.src.data.language_registry_loader import get_cellar_uri

SPARQL_ENDPOINT = "https://publications.europa.eu/webapi/rdf/sparql"
DEFAULT_LIMIT = 100
MAX_RETRIES = 3


class SparqlClient:
    """Queries CELLAR metadata via SPARQL 1.1."""

    def __init__(self, timeout: float = 55.0) -> None:
        self._timeout = timeout

    async def execute(self, query: str) -> dict[str, Any]:
        for attempt in range(MAX_RETRIES):
            try:
                async with httpx.AsyncClient(timeout=self._timeout) as client:
                    response = await client.get(
                        SPARQL_ENDPOINT,
                        params={"query": query},
                        headers={"Accept": "application/sparql-results+json"},
                    )
                    if response.status_code in (429, 503):
                        await asyncio.sleep(2 ** attempt)
                        continue
                    response.raise_for_status()
                    return response.json()
            except Exception as exc:
                logger.warning("SPARQL request failed (attempt %s): %s", attempt + 1, exc)
                if attempt == MAX_RETRIES - 1:
                    raise
                await asyncio.sleep(2 ** attempt)
        return {"results": {"bindings": []}}

    async def fetch_work_by_celex(self, celex: str, language: str = "nl") -> dict[str, str] | None:
        lang_uri = get_cellar_uri(language)
        query = f"""
        PREFIX cdm: <http://publications.europa.eu/ontology/cdm#>
        SELECT ?title ?modified WHERE {{
          ?work cdm:work_id_celex "{celex}" .
          OPTIONAL {{ ?work cdm:work_date_document ?modified }}
          OPTIONAL {{
            ?expr cdm:expression_belongs_to_work ?work .
            ?expr cdm:expression_title ?title .
            ?expr cdm:expression_uses_language
              <http://publications.europa.eu/resource/authority/language/{lang_uri}>
          }}
        }} LIMIT 1
        """
        rows = self._parse_bindings(await self.execute(query))
        return rows[0] if rows else None

    async def discover_celex_by_keywords(
        self,
        question: str,
        language: str = "nl",
    ) -> str | None:
        candidates = await self.discover_celex_candidates(question, language, limit=1)
        if not candidates:
            return None
        return candidates[0].get("celex") or None

    async def discover_celex_candidates(
        self,
        question: str,
        language: str = "nl",
        limit: int = 10,
    ) -> list[dict[str, str | float]]:
        terms = self._discovery_terms(question)
        if not terms:
            return []
        lang_uri = get_cellar_uri(language)
        filters = " || ".join(
            f'CONTAINS(LCASE(STR(?title)), "{term}")' for term in terms
        )
        query = f"""
        PREFIX cdm: <http://publications.europa.eu/ontology/cdm#>
        SELECT ?celex ?title WHERE {{
          ?work a cdm:legislation .
          ?work cdm:work_id_celex ?celex .
          ?expr cdm:expression_belongs_to_work ?work .
          ?expr cdm:expression_title ?title .
          ?expr cdm:expression_uses_language
            <http://publications.europa.eu/resource/authority/language/{lang_uri}> .
          FILTER({filters})
        }} LIMIT {max(limit, 10)}
        """
        rows = self._parse_bindings(await self.execute(query))
        return self._rank_discovery_rows(rows, terms)[:limit]

    def _discovery_terms(self, question: str) -> list[str]:
        stopwords = {
            "welke", "welk", "wat", "hoe", "legt", "leggen", "op", "aan", "van",
            "voor", "bij", "met", "zonder", "de", "het", "een", "die", "richtlijn",
            "verordening", "europese", "european", "union", "unie",
        }
        terms = [
            term.lower()
            for term in re.findall(r"[A-Za-zÀ-ÿ]{4,}", question)
            if term.lower() not in stopwords
        ]
        return terms[:5]

    def _rank_discovery_rows(
        self,
        rows: list[dict[str, str]],
        terms: list[str],
    ) -> list[dict[str, str | float]]:
        ranked: list[tuple[float, dict[str, str | float]]] = []
        for row in rows:
            celex = row.get("celex", "")
            title = row.get("title", "")
            if not celex:
                continue
            title_lower = title.lower()
            hits = sum(1 for term in terms if term in title_lower)
            score = hits / max(len(terms), 1)
            if hits == len(terms) and terms:
                score = min(1.0, score + 0.2)
            ranked.append((score, {"celex": celex, "title": title, "score": round(score, 3)}))
        ranked.sort(key=lambda pair: pair[0], reverse=True)
        return [item for _, item in ranked]

    async def fetch_works_page(
        self, offset: int = 0, limit: int = DEFAULT_LIMIT
    ) -> list[dict[str, str]]:
        query = self._works_query(offset, limit)
        result = await self.execute(query)
        return self._parse_bindings(result)

    async def fetch_modified_since(
        self, date_str: str, offset: int = 0, limit: int = DEFAULT_LIMIT
    ) -> list[dict[str, str]]:
        query = self._modified_query(date_str, offset, limit)
        result = await self.execute(query)
        return self._parse_bindings(result)

    async def fetch_document_relations(self, celex: str) -> list[dict[str, str]]:
        query = f"""
        PREFIX cdm: <http://publications.europa.eu/ontology/cdm#>
        SELECT ?relation ?target ?type WHERE {{
          ?work cdm:work_id_celex "{celex}" .
          ?work ?relation ?target .
          FILTER(STRSTARTS(STR(?relation), STR(cdm:)))
          OPTIONAL {{ ?target a ?type }}
        }} LIMIT 50
        """
        result = await self.execute(query)
        return self._parse_bindings(result)

    def _works_query(self, offset: int, limit: int) -> str:
        return f"""
        PREFIX cdm: <http://publications.europa.eu/ontology/cdm#>
        SELECT ?celex ?title ?modified WHERE {{
          ?work a cdm:legislation .
          ?work cdm:work_id_celex ?celex .
          ?work cdm:work_date_document ?modified .
          OPTIONAL {{ ?expr cdm:expression_belongs_to_work ?work .
                     ?expr cdm:expression_title ?title .
                     ?expr cdm:expression_uses_language
                       <http://publications.europa.eu/resource/authority/language/NLD> }}
        }} ORDER BY ?celex OFFSET {offset} LIMIT {limit}
        """

    def _modified_query(self, date_str: str, offset: int, limit: int) -> str:
        return f"""
        PREFIX cdm: <http://publications.europa.eu/ontology/cdm#>
        SELECT ?celex ?modified WHERE {{
          ?work a cdm:legislation .
          ?work cdm:work_id_celex ?celex .
          ?work cdm:work_date_document ?modified .
          FILTER(?modified >= "{date_str}"^^xsd:date)
        }} ORDER BY ?modified OFFSET {offset} LIMIT {limit}
        """

    def _parse_bindings(self, result: dict[str, Any]) -> list[dict[str, str]]:
        bindings = result.get("results", {}).get("bindings", [])
        rows = []
        for row in bindings:
            rows.append({k: v.get("value", "") for k, v in row.items()})
        return rows

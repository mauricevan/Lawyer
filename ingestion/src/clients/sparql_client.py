"""CELLAR SPARQL endpoint client with pagination."""
import logging
from typing import Any
from urllib.parse import urlencode

import httpx

logger = logging.getLogger(__name__)

SPARQL_ENDPOINT = "https://publications.europa.eu/webapi/rdf/sparql"
DEFAULT_LIMIT = 100


class SparqlClient:
    """Queries CELLAR metadata via SPARQL 1.1."""

    def __init__(self, timeout: float = 55.0) -> None:
        self._timeout = timeout

    async def execute(self, query: str) -> dict[str, Any]:
        async with httpx.AsyncClient(timeout=self._timeout) as client:
            response = await client.get(
                SPARQL_ENDPOINT,
                params={"query": query},
                headers={"Accept": "application/sparql-results+json"},
            )
            response.raise_for_status()
            return response.json()

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

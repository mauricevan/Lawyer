"""Bulk RDF dump loader for large-scale EUR-Lex ingestion (fase 4+)."""
import logging
import os
from pathlib import Path
from typing import AsyncIterator

import httpx

logger = logging.getLogger(__name__)

EU_DATA_PORTAL = "https://data.europa.eu/api/hub/search/datasets"


class DumpLoader:
    """Downloads and streams EUR-Lex bulk RDF packages."""

    def __init__(self, cache_dir: str = "data/raw") -> None:
        self._cache_dir = Path(cache_dir)
        self._cache_dir.mkdir(parents=True, exist_ok=True)

    async def list_available_dumps(self) -> list[dict[str, str]]:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(
                EU_DATA_PORTAL,
                params={"q": "EUR-Lex CELLAR", "limit": 10},
            )
            response.raise_for_status()
            data = response.json()
            return [
                {"title": r.get("title", ""), "id": r.get("id", "")}
                for r in data.get("result", {}).get("results", [])
            ]

    async def download_dump(self, url: str, filename: str) -> Path:
        dest = self._cache_dir / filename
        if dest.exists():
            logger.info("Using cached dump: %s", dest)
            return dest
        async with httpx.AsyncClient(timeout=600.0) as client:
            async with client.stream("GET", url) as response:
                response.raise_for_status()
                with open(dest, "wb") as f:
                    async for chunk in response.aiter_bytes(chunk_size=65536):
                        f.write(chunk)
        return dest

    def iter_rdf_file(self, path: Path) -> AsyncIterator[str]:
        """Stream-parse RDF file line by line (placeholder for SAX parser)."""
        async def _gen() -> AsyncIterator[str]:
            with open(path, "r", encoding="utf-8", errors="replace") as f:
                for line in f:
                    yield line
        return _gen()

    @staticmethod
    def requires_eu_login() -> bool:
        return bool(os.getenv("EU_LOGIN_EMAIL"))

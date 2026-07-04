#!/usr/bin/env python3
"""Build CELEX title index JSON from curated corpus and SPARQL."""
import argparse
import asyncio
import json
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from ingestion.src.clients.sparql_client import SparqlClient
from ingestion.src.data.curated_loader import load_curated_documents

logger = logging.getLogger(__name__)
DEFAULT_OUTPUT = Path(__file__).resolve().parents[1] / "data" / "celex_title_index.json"


def _curated_entries() -> list[dict]:
    entries: list[dict] = []
    seen: set[str] = set()
    for document in load_curated_documents():
        if document.celex in seen:
            continue
        seen.add(document.celex)
        aliases = [document.short_title] if document.short_title else []
        entries.append({"celex": document.celex, "title": document.title, "aliases": aliases})
    return entries


async def _sparql_entries(limit_pages: int, page_size: int) -> list[dict]:
    client = SparqlClient()
    entries: list[dict] = []
    seen: set[str] = set()
    for page in range(limit_pages):
        rows = await client.fetch_works_page(offset=page * page_size, limit=page_size)
        if not rows:
            break
        for row in rows:
            celex = row.get("celex", "")
            title = row.get("title", "")
            if not celex or celex in seen or not title:
                continue
            seen.add(celex)
            entries.append({"celex": celex, "title": title, "aliases": []})
    return entries


async def run_build(output: Path, sparql_pages: int, page_size: int) -> int:
    merged: dict[str, dict] = {}
    for entry in _curated_entries():
        merged[entry["celex"]] = entry
    if sparql_pages > 0:
        for entry in await _sparql_entries(sparql_pages, page_size):
            merged.setdefault(entry["celex"], entry)
    payload = {"entries": list(merged.values())}
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    logger.info("Wrote %d entries to %s", len(payload["entries"]), output)
    return len(payload["entries"])


def main() -> None:
    logging.basicConfig(level=logging.INFO)
    parser = argparse.ArgumentParser(description="Build CELEX title index JSON")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--sparql-pages", type=int, default=0, help="SPARQL pages to fetch (0=curated only)")
    parser.add_argument("--page-size", type=int, default=100)
    args = parser.parse_args()
    count = asyncio.run(run_build(args.output, args.sparql_pages, args.page_size))
    print(f"Built index with {count} entries → {args.output}")


if __name__ == "__main__":
    main()

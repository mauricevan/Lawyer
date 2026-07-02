"""Load curated EUR-Lex document metadata from YAML."""
from pathlib import Path

import yaml

from shared.schemas.document import DocumentMetadata, VersionType

_CURATED_PATH = Path(__file__).parent / "curated_celex.yaml"


def _parse_version_type(value: str) -> VersionType:
    return VersionType(value)


def load_curated_documents(path: Path | None = None) -> list[DocumentMetadata]:
    """Parse curated_celex.yaml into DocumentMetadata objects."""
    source = path or _CURATED_PATH
    with open(source, encoding="utf-8") as handle:
        data = yaml.safe_load(handle)
    documents: list[DocumentMetadata] = []
    seen_celex: set[str] = set()
    for entry in data.get("documents", []):
        celex = entry["celex"]
        if celex in seen_celex:
            continue
        seen_celex.add(celex)
        documents.append(
            DocumentMetadata(
                celex=entry["celex"],
                title=entry["title"],
                short_title=entry.get("short_title"),
                doc_type=entry.get("doc_type", "regulation"),
                language=entry.get("language", "nl"),
                is_in_force=entry.get("is_in_force", True),
                is_consolidated=entry.get("is_consolidated", False),
                version_type=_parse_version_type(entry.get("version_type", "base")),
                eli_uri=entry.get("eli_uri"),
                oj_reference=entry.get("oj_reference"),
                corrigendum_celex=entry.get("corrigendum_celex"),
            )
        )
    return documents


def load_documents_by_cluster(cluster: str, path: Path | None = None) -> list[DocumentMetadata]:
    """Return documents belonging to a named cluster."""
    source = path or _CURATED_PATH
    with open(source, encoding="utf-8") as handle:
        data = yaml.safe_load(handle)
    celex_set = set(data.get("clusters", {}).get(cluster, []))
    return [doc for doc in load_curated_documents(source) if doc.celex in celex_set]

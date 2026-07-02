"""Load multilingual EUR-Lex seed documents for plan11 AA."""
from pathlib import Path

import yaml

from shared.schemas.document import DocumentMetadata, VersionType

_SEED_PATH = Path(__file__).parent / "multilingual_seed.yaml"


def _parse_version_type(value: str) -> VersionType:
    return VersionType(value)


def load_multilingual_seed_documents(
    languages: tuple[str, ...] | None = None,
    path: Path | None = None,
) -> list[DocumentMetadata]:
    """Build DocumentMetadata per CELEX and target language."""
    source = path or _SEED_PATH
    with open(source, encoding="utf-8") as handle:
        data = yaml.safe_load(handle)
    target_langs = languages or tuple(data.get("languages", []))
    documents: list[DocumentMetadata] = []
    for entry in data.get("documents", []):
        titles = entry.get("titles", {})
        for lang in target_langs:
            title = titles.get(lang) or titles.get("en") or entry.get("short_title", entry["celex"])
            documents.append(
                DocumentMetadata(
                    celex=entry["celex"],
                    title=title,
                    short_title=entry.get("short_title"),
                    doc_type=entry.get("doc_type", "regulation"),
                    language=lang,
                    is_in_force=entry.get("is_in_force", True),
                    is_consolidated=entry.get("is_consolidated", True),
                    version_type=_parse_version_type(entry.get("version_type", "consolidated")),
                    oj_reference=entry.get("oj_reference"),
                )
            )
    return documents

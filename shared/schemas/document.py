"""Document type and version enums."""
from datetime import datetime
from enum import Enum
from typing import Literal

from pydantic import BaseModel, Field


class VersionType(str, Enum):
    BASE = "base"
    CONSOLIDATED = "consolidated"
    CORRIGENDUM = "corrigendum"
    AMENDMENT = "amendment"


DocType = Literal[
    "regulation", "directive", "decision", "case_law", "preparatory", "oj"
]


class DocumentMetadata(BaseModel):
    """Metadata for an EUR-Lex document work."""

    celex: str
    cellar_id: str | None = None
    eli_uri: str | None = None
    doc_type: DocType = "regulation"
    language: str = "nl"
    title: str
    short_title: str | None = None
    is_in_force: bool = True
    is_consolidated: bool = False
    version_type: VersionType = VersionType.BASE
    modified_at: datetime | None = None
    oj_reference: str | None = None
    corrigendum_celex: str | None = None


class DocumentChunk(BaseModel):
    """A searchable chunk of legal text."""

    chunk_id: str
    celex: str
    text: str
    article_number: str | None = None
    subdivision_type: str = "article"
    language: str = "nl"
    version_type: VersionType = VersionType.BASE
    is_consolidated: bool = False
    is_in_force: bool = True
    eli_uri: str | None = None
    title: str | None = None
    oj_reference: str | None = None
    text_hash: str | None = None

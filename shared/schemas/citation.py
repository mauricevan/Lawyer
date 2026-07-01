"""Citation and trust indicator schemas."""
from datetime import date

from pydantic import BaseModel, Field


class TrustIndicator(BaseModel):
    """Visual trust metadata for a legal citation."""

    is_consolidated: bool = False
    is_in_force: bool = True
    last_modified: date | None = None
    oj_reference: str | None = None
    has_corrigendum: bool = False
    corrigendum_celex: str | None = None
    has_amendment: bool = False
    amendment_celex: str | None = None


class Citation(BaseModel):
    """A source citation with trust indicators."""

    celex: str
    article: str | None = None
    title: str | None = None
    excerpt: str = ""
    eli_uri: str | None = None
    eurlex_url: str = ""
    trust: TrustIndicator = Field(default_factory=TrustIndicator)
    legal_citation: str = ""

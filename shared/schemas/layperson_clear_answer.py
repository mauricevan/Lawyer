"""Structured layperson answer model — antwoord-eerst format (ADR layperson clarity)."""
from pydantic import BaseModel, Field


class ObligationRow(BaseModel):
    """One practical obligation row for the practice table."""

    label: str
    uitleg: str


class ArticleSummary(BaseModel):
    """Plain-language summary of one legal article."""

    article: str
    title: str = ""
    uitleg_nl: str


class TermDefinition(BaseModel):
    """One-line definition of a legal term."""

    term: str
    definition_nl: str


class OfficialExcerpt(BaseModel):
    """Short verbatim excerpt for collapsible official text block."""

    article: str = ""
    label: str = ""
    text: str


class LaypersonClearAnswer(BaseModel):
    """Canonical layperson answer before markdown rendering."""

    kort_antwoord: str
    obligations: list[ObligationRow] = Field(default_factory=list)
    voorbeeld: str = ""
    juridische_basis: list[ArticleSummary] = Field(default_factory=list)
    begrippen: list[TermDefinition] = Field(default_factory=list)
    let_op: str = ""
    official_excerpts: list[OfficialExcerpt] = Field(default_factory=list)

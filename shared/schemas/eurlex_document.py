"""EUR-Lex live document session — parsed articles from a fetched act."""
from pydantic import BaseModel, Field


class EurlexArticle(BaseModel):
    """Single article body from a live EUR-Lex fetch."""

    article_number: str
    title: str = ""
    text: str
    subdivision_type: str = "article"


class EurlexDocumentSession(BaseModel):
    """In-memory view of one CELEX act after live fetch + parse."""

    celex: str
    title: str
    language: str
    articles: dict[str, EurlexArticle] = Field(default_factory=dict)
    article_count: int = 0
    fetch_source: str = "eurlex_research"
    is_consolidated: bool = False

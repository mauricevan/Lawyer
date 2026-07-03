"""Query routing decision model (plan12 AC)."""
from dataclasses import dataclass, field


@dataclass(slots=True)
class QueryRoute:
    """Structured route decision used by retrieval."""

    domains: list[str] = field(default_factory=list)
    doc_types: list[str] = field(default_factory=list)
    time_context: str = "current"
    keywords: list[str] = field(default_factory=list)
    celex_hint: str | None = None
    language: str = "nl"
    intent_id: str | None = None
    confidence: float = 0.5
    domain_cluster: str | None = None

    def as_dict(self) -> dict[str, object]:
        return {
            "domains": self.domains,
            "doc_types": self.doc_types,
            "time_context": self.time_context,
            "keywords": self.keywords,
            "celex_hint": self.celex_hint,
            "language": self.language,
            "intent_id": self.intent_id,
            "confidence": self.confidence,
            "domain_cluster": self.domain_cluster,
        }

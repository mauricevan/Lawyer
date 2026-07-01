"""Trust indicators for legal citations — version confidence."""
from datetime import date

from shared.schemas.citation import Citation, TrustIndicator
from shared.schemas.document import DocumentMetadata, VersionType


class TrustIndicatorService:
    """Builds trust metadata and applies retrieval preferences."""

    def build_trust(self, metadata: DocumentMetadata) -> TrustIndicator:
        return TrustIndicator(
            is_consolidated=metadata.is_consolidated,
            is_in_force=metadata.is_in_force,
            last_modified=metadata.modified_at.date() if metadata.modified_at else None,
            oj_reference=metadata.oj_reference,
            has_corrigendum=metadata.version_type == VersionType.CORRIGENDUM
            or metadata.corrigendum_celex is not None,
            corrigendum_celex=metadata.corrigendum_celex,
            has_amendment=metadata.version_type == VersionType.AMENDMENT,
        )

    def build_from_payload(self, payload: dict) -> TrustIndicator:
        return TrustIndicator(
            is_consolidated=payload.get("is_consolidated", False),
            is_in_force=payload.get("is_in_force", True),
            oj_reference=payload.get("oj_reference"),
            has_corrigendum=payload.get("version_type") == "corrigendum",
        )

    def prefer_consolidated(self, results: list[dict]) -> list[dict]:
        consolidated = [r for r in results if r.get("is_consolidated")]
        if consolidated:
            return consolidated + [r for r in results if not r.get("is_consolidated")]
        return results

    def enrich_citation(self, citation: Citation, payload: dict) -> Citation:
        from backend.src.services.citation_formatter import CitationFormatter

        citation.trust = self.build_from_payload(payload)
        citation.legal_citation = CitationFormatter().to_legal_format(citation)
        return citation

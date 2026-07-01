"""Unit tests for TrustIndicatorService."""
from backend.src.services.trust_indicator_service import TrustIndicatorService
from shared.schemas.document import DocumentMetadata, VersionType


def test_prefer_consolidated_over_base() -> None:
    service = TrustIndicatorService()
    results = [
        {"celex": "32016R0679", "is_consolidated": False, "text": "base"},
        {"celex": "32016R0679", "is_consolidated": True, "text": "consolidated"},
    ]
    ordered = service.prefer_consolidated(results)
    assert ordered[0]["is_consolidated"] is True


def test_build_trust_from_metadata() -> None:
    service = TrustIndicatorService()
    meta = DocumentMetadata(
        celex="32024R1689",
        cellar_id=None,
        title="AI Act",
        is_consolidated=True,
        is_in_force=True,
        version_type=VersionType.CONSOLIDATED,
        oj_reference="L 2024/1689",
        corrigendum_celex="32024R1689R(01)",
    )
    trust = service.build_trust(meta)
    assert trust.is_consolidated is True
    assert trust.has_corrigendum is True

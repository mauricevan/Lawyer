"""Tests for citation/source consistency checks."""
from shared.schemas.citation import Citation
from backend.src.services.source_consistency_service import SourceConsistencyService


def test_filters_citations_not_in_context():
    service = SourceConsistencyService()
    citations = [
        Citation(celex="32022R2554", excerpt="a"),
        Citation(celex="99999X9999", excerpt="b"),
    ]
    context = [{"celex": "32022R2554", "text": "dora"}]
    filtered = service.filter_citations(citations, context)
    assert len(filtered) == 1
    assert filtered[0].celex == "32022R2554"


def test_find_invalid_citations():
    service = SourceConsistencyService()
    citations = [Citation(celex="99999X9999", excerpt="x")]
    invalid = service.find_invalid_citations(citations, [{"celex": "32022R2554"}])
    assert invalid == ["99999X9999"]

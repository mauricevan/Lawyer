"""Unit tests for version conflict resolution (plan13 AD)."""
from backend.src.services.document_version_conflict_service import DocumentVersionConflictService
from backend.src.utils.document_version_utils import extract_base_celex, version_priority_rank
from shared.schemas.query import QueryFilters


def test_extract_base_celex_strips_corrigendum_suffix():
    assert extract_base_celex("32024R1689R(01)") == "32024R1689"


def test_consolidated_outranks_corrigendum():
    assert version_priority_rank("consolidated") > version_priority_rank("corrigendum")


def test_resolve_retrieval_chunks_prefers_consolidated():
    service = DocumentVersionConflictService()
    chunks = [
        {"chunk_id": "a", "celex": "32024R1689", "version_type": "consolidated", "language": "nl"},
        {"chunk_id": "b", "celex": "32024R1689R(01)", "version_type": "corrigendum", "language": "nl"},
    ]
    resolved = service.resolve_retrieval_chunks(chunks, None)
    assert len(resolved) == 1
    assert resolved[0]["celex"] == "32024R1689"


def test_explicit_celex_keeps_corrigendum():
    service = DocumentVersionConflictService()
    chunks = [
        {"chunk_id": "a", "celex": "32024R1689", "version_type": "consolidated", "language": "nl"},
        {"chunk_id": "b", "celex": "32024R1689R(01)", "version_type": "corrigendum", "language": "nl"},
    ]
    filters = QueryFilters(celex="32024R1689R(01)")
    resolved = service.resolve_retrieval_chunks(chunks, filters)
    assert len(resolved) == 2


def test_scan_curated_detects_ai_act_family():
    service = DocumentVersionConflictService()
    conflicts = service.scan_curated()
    bases = {row.base_celex for row in conflicts}
    assert "32024R1689" in bases


def test_validate_registered_families_passes_for_ai_act():
    result = DocumentVersionConflictService().validate_registered_families()
    assert result["passed"] is True
    assert "32024R1689" in result["registered"]

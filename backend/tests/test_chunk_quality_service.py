"""Tests for chunk quality filtering."""
from backend.src.services.chunk_quality_service import ChunkQualityService


def test_rejects_short_chunks():
    service = ChunkQualityService()
    chunks = [{"text": "short", "chunk_id": "1"}]
    assert service.filter_chunks(chunks) == []


def test_rejects_navigation_html_chunks():
    service = ChunkQualityService()
    text = "Skip to main content My EUR-Lex sign in register javascript: click here " * 3
    chunks = [{"text": text, "chunk_id": "1"}]
    assert service.filter_chunks(chunks) == []


def test_accepts_valid_legal_chunk():
    service = ChunkQualityService()
    text = "Financial entities shall maintain ICT risk management frameworks with documented policies."
    chunks = [{"text": text, "chunk_id": "1"}]
    assert len(service.filter_chunks(chunks)) == 1


def test_accepts_gpsr_chunk_with_celex_prefix():
    service = ChunkQualityService()
    text = (
        "CELEX:32023R0988 | L_2023135NL.01000101.xml | Artikel 9 | article\n"
        "Artikel 9 Verplichtingen van fabrikanten. Wanneer een product een risico vormt, "
        "stelt de fabrikant onverwijld de bevoegde autoriteiten op de hoogte en neemt "
        "corrigerende maatregelen zonder onnodige vertraging."
    )
    kept = service.filter_chunks([{"text": text, "chunk_id": "1", "article_number": "9"}])
    assert len(kept) == 1
    assert ".xml" not in kept[0]["text"]
    assert "fabrikant" in kept[0]["text"].lower()

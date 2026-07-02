"""Tests for curated document loader."""
from ingestion.src.data.curated_loader import load_curated_documents, load_documents_by_cluster


def test_load_curated_documents_unique_celex():
    documents = load_curated_documents()
    celexes = [doc.celex for doc in documents]
    assert len(documents) >= 100
    assert len(celexes) == len(set(celexes))


def test_load_documents_by_cluster_ai_digital():
    documents = load_documents_by_cluster("ai_digital")
    assert any(doc.celex == "32024R1689" for doc in documents)
    assert all(doc.celex for doc in documents)

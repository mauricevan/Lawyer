"""Tests for multilingual seed loader (plan11 AA)."""
from ingestion.src.data.multilingual_loader import load_multilingual_seed_documents


def test_loads_nine_documents_for_fr_de_es() -> None:
    docs = load_multilingual_seed_documents(languages=("fr", "de", "es"))
    assert len(docs) == 9
    langs = {doc.language for doc in docs}
    assert langs == {"fr", "de", "es"}


def test_gdpr_french_title() -> None:
    docs = load_multilingual_seed_documents(languages=("fr",))
    gdpr = [doc for doc in docs if doc.celex == "32016R0679"][0]
    assert gdpr.language == "fr"
    assert "2016/679" in gdpr.title

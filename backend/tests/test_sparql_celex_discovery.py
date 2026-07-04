"""Unit tests for ranked SPARQL CELEX discovery."""
import pytest

from ingestion.src.clients.sparql_client import SparqlClient


def test_discovery_terms_filters_stopwords():
    client = SparqlClient()
    terms = client._discovery_terms(
        "Welke verplichtingen legt de Europese Milieuaansprakelijkheidsrichtlijn op?"
    )
    assert "welke" not in terms
    assert "richtlijn" not in terms
    assert any("milieuaansprakelijk" in term for term in terms)


def test_rank_discovery_rows_orders_by_overlap():
    client = SparqlClient()
    rows = [
        {"celex": "32004L0035", "title": "Richtlijn milieuaansprakelijkheid milieuschade"},
        {"celex": "32016R0679", "title": "Algemene verordening gegevensbescherming"},
    ]
    terms = ["milieuaansprakelijkheid", "milieuschade"]
    ranked = client._rank_discovery_rows(rows, terms)
    assert ranked[0]["celex"] == "32004L0035"
    assert ranked[0]["score"] > ranked[1]["score"]

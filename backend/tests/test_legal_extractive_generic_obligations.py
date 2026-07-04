"""Tests for obligation-based generic extractive excerpts."""
from backend.src.services.legal_extractive_generic import (
    can_build_generic_answer,
    collect_generic_excerpts,
)


def test_collect_excerpts_without_article_number_when_obligations_present():
    chunks = [{
        "celex": "32004L0035",
        "title": "Milieuaansprakelijkheid",
        "text": (
            "De exploitant is verplicht onmiddellijk maatregelen te nemen om milieuschade "
            "te voorkomen, te beheersen en te herstellen wanneer een dreiging van schade "
            "aan het milieu ontstaat door zijn activiteiten."
        ) * 2,
    }]
    excerpts = collect_generic_excerpts(chunks, "verplichtingen milieuschade", limit=2)
    assert len(excerpts) == 1
    assert excerpts[0]["celex"] == "32004L0035"
    assert "verplicht" in excerpts[0]["text"].lower()


def test_can_build_generic_answer_with_obligation_chunks():
    chunks = [{
        "celex": "32004L0035",
        "text": "Exploitanten zijn aansprakelijk voor milieuschade en moeten herstelmaatregelen treffen." * 4,
    }]
    assert can_build_generic_answer(chunks, "milieuaansprakelijkheid verplichtingen")

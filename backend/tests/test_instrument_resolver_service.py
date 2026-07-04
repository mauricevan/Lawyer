"""Tests for instrument resolver CELEX resolution."""
import pytest

from backend.src.services.celex_discovery_service import CelexCandidate
from backend.src.services.instrument_resolver_service import InstrumentResolverService
from shared.schemas.legal_interpretation import InstrumentTarget, LegalInterpretationPlan


@pytest.mark.asyncio
async def test_resolve_oj_citation_to_reach_celex(monkeypatch):
    resolver = InstrumentResolverService()

    async def mock_discover(_text, _lang, limit=1):
        return []

    async def mock_title(celex, _lang):
        return {"title": f"Title for {celex}"}

    monkeypatch.setattr(resolver._discovery, "discover", mock_discover)
    monkeypatch.setattr(resolver._sparql, "fetch_work_by_celex", mock_title)
    plan = LegalInterpretationPlan(
        instruments=[InstrumentTarget(name="REACH", articles=["6"], confidence=0.9)],
        search_keywords=["registratie"],
    )
    question = "Registratie volgens Verordening (EG) nr. 1907/2006"
    resolved = await resolver.resolve(plan, question, "nl")
    assert resolved.instruments[0].celex == "32006R1907"


@pytest.mark.asyncio
async def test_resolve_via_discovery_when_no_oj(monkeypatch):
    resolver = InstrumentResolverService()

    async def mock_discover(_text, _lang, limit=1):
        return [CelexCandidate(celex="32004L0035", score=0.9, source="title_index", title="Milieu")]

    async def mock_title(celex, _lang):
        return {"title": "Milieuaansprakelijkheid"}

    monkeypatch.setattr(resolver._discovery, "discover", mock_discover)
    monkeypatch.setattr(resolver._sparql, "fetch_work_by_celex", mock_title)
    plan = LegalInterpretationPlan(
        instruments=[InstrumentTarget(name="milieuaansprakelijkheid", confidence=0.7)],
    )
    resolved = await resolver.resolve(plan, "Wat is milieuaansprakelijkheid?", "nl")
    assert resolved.instruments[0].celex == "32004L0035"
    assert resolved.instruments[0].title == "Milieuaansprakelijkheid"

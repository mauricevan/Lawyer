"""Tests for discovery merge in CELEX hint resolver."""
from backend.src.utils.celex_hint_resolver import (
    merge_discovery_celex_set,
    resolve_discovery_candidates,
    resolve_live_celex_hint,
)

ENV_QUESTION = (
    "Welke verplichtingen legt de Europese Milieuaansprakelijkheidsrichtlijn "
    "op aan exploitanten die milieuschade veroorzaken?"
)


def test_resolve_discovery_candidates_returns_milieu_celex():
    hits = resolve_discovery_candidates(ENV_QUESTION)
    assert hits
    assert hits[0].celex == "32004L0035"


def test_merge_discovery_celex_set_includes_discovery():
    merged = merge_discovery_celex_set(ENV_QUESTION)
    assert "32004L0035" in merged


def test_resolve_live_celex_hint_uses_discovery_before_planner():
    celex = resolve_live_celex_hint(ENV_QUESTION, None, None)
    assert celex == "32004L0035"

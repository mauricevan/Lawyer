"""Tests for legal domain retrieval filter."""
from backend.src.utils.legal_domain_retrieval_filter import (
    filter_instruments_by_domain,
    is_celex_allowed_for_domain,
)
from shared.schemas.legal_interpretation import InstrumentTarget


def test_blocks_mar_for_administrative_law():
    assert not is_celex_allowed_for_domain("32014R0596", "administrative_law")


def test_blocks_customs_for_employment():
    assert not is_celex_allowed_for_domain("32013R0952", "employment_law")


def test_blocks_customs_for_internal_market_product():
    assert not is_celex_allowed_for_domain("32013R0952", "internal_market")


def test_allows_gpsr_for_product_safety():
    assert is_celex_allowed_for_domain("32023R0988", "product_safety")


def test_allows_internal_market_celex():
    assert is_celex_allowed_for_domain("32008R0768", "internal_market")


def test_default_instrument_for_internal_market():
    from backend.src.utils.legal_domain_retrieval_filter import default_instrument_for_domain

    inst = default_instrument_for_domain("internal_market", "Mag een lidstaat nationale regels afwijken?")
    assert inst is not None
    assert inst.celex == "32008R0768"
    assert inst.name == "internal_market_national_rules"


def test_filter_instruments_removes_mar():
    instruments = [
        InstrumentTarget(name="mar", celex="32014R0596", confidence=0.5),
        InstrumentTarget(name="surveillance", celex="32019R1020", confidence=0.6),
    ]
    kept = filter_instruments_by_domain(instruments, "administrative_law")
    assert len(kept) == 1
    assert kept[0].celex == "32019R1020"

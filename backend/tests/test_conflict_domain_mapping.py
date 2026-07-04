"""Tests for V4 conflict → domain mapping."""
from backend.src.utils.conflict_domain_mapping import (
    is_celex_allowed_for_conflict,
    map_conflict_to_domain,
)


def test_internal_market_blocks_dsa_celex():
    assert is_celex_allowed_for_conflict("32022R2065", "internal_market_restriction") is False
    assert is_celex_allowed_for_conflict("32000L0031", "internal_market_restriction") is True


def test_platform_conflict_allows_dsa():
    assert is_celex_allowed_for_conflict("32022R2065", "platform_governance_issue") is True


def test_consumer_mapping_celex():
    mapping = map_conflict_to_domain("consumer_transaction_issue")
    assert mapping.domain == "consumer_protection"
    assert mapping.default_celex == "32011L0083"

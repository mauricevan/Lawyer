"""Allowed and forbidden CELEX sets per primary legal conflict — V5.1."""
from shared.schemas.legal_conflict import PrimaryLegalConflict

_CUSTOMS = frozenset({"32013R0952", "32015R2446"})
_FINANCE = frozenset({"32014R0596"})
_DSA = frozenset({"32022R2065"})
_CONSUMER = frozenset({"32011L0083", "32019L0771"})
_GDPR = frozenset({"32016R0679"})
_SURVEILLANCE = frozenset({"32019R1020"})
_ECOMMERCE = frozenset({"32000L0031"})
_MUTUAL_RECOGNITION = frozenset({"32008R0768"})
_EMPLOYMENT = frozenset({"32000L0078"})
_GPSR = frozenset({"32023R0988"})

_CONFLICT_PRIMARY_CELEX: dict[PrimaryLegalConflict, tuple[str, ...]] = {
    "internal_market_restriction": ("32000L0031", "32008R0768"),
    "consumer_transaction_issue": ("32011L0083",),
    "employment_relationship_issue": ("32000L0078",),
    "data_processing_issue": ("32016R0679",),
    "product_compliance_issue": ("32023R0988",),
    "administrative_enforcement_issue": ("32019R1020",),
    "platform_governance_issue": ("32022R2065",),
}

_CONFLICT_ALLOWED_CELEX: dict[PrimaryLegalConflict, frozenset[str]] = {
    "internal_market_restriction": _ECOMMERCE | _MUTUAL_RECOGNITION | _SURVEILLANCE,
    "consumer_transaction_issue": _CONSUMER | _ECOMMERCE,
    "employment_relationship_issue": _EMPLOYMENT,
    "data_processing_issue": _GDPR,
    "product_compliance_issue": _GPSR | _SURVEILLANCE,
    "administrative_enforcement_issue": _SURVEILLANCE | _GPSR,
    "platform_governance_issue": _DSA,
}

_CONFLICT_FORBIDDEN_CELEX: dict[PrimaryLegalConflict, frozenset[str]] = {
    "internal_market_restriction": _CUSTOMS | _FINANCE | _DSA | _CONSUMER | _GDPR | _EMPLOYMENT,
    "consumer_transaction_issue": _DSA | _CUSTOMS | _FINANCE | _EMPLOYMENT,
    "employment_relationship_issue": _DSA | _CONSUMER | _GPSR | _CUSTOMS,
    "data_processing_issue": _DSA | _CONSUMER | _EMPLOYMENT,
    "product_compliance_issue": _DSA | _CONSUMER | _EMPLOYMENT | _FINANCE,
    "administrative_enforcement_issue": _DSA | _CONSUMER | _EMPLOYMENT | _FINANCE,
    "platform_governance_issue": _CONSUMER | _EMPLOYMENT | _CUSTOMS,
}


def primary_celex_for_conflict(conflict: PrimaryLegalConflict) -> tuple[str, ...]:
    """CELEX with highest juridical priority for a conflict."""
    return _CONFLICT_PRIMARY_CELEX[conflict]


def is_celex_allowed_for_conflict_type(celex: str, conflict: PrimaryLegalConflict) -> bool:
    """Return False when CELEX is explicitly forbidden for this conflict."""
    if celex in _CONFLICT_FORBIDDEN_CELEX.get(conflict, frozenset()):
        return False
    allowed = _CONFLICT_ALLOWED_CELEX.get(conflict, frozenset())
    return celex in allowed


def conflict_celex_candidates(conflict: PrimaryLegalConflict) -> frozenset[str]:
    """All CELEX that may be scored for a conflict."""
    return _CONFLICT_ALLOWED_CELEX.get(conflict, frozenset())

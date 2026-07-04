"""Deterministic V4 mapping: primary legal conflict → domain + EU frameworks."""
from dataclasses import dataclass

from shared.schemas.legal_conflict import PrimaryLegalConflict
from shared.schemas.legal_interpretation import LegalRoutingDomain

_DSA_CELEX = frozenset({"32022R2065"})
_GDPR_CELEX = frozenset({"32016R0679"})


@dataclass(frozen=True)
class ConflictDomainMapping:
    """Single routing target for a primary legal conflict."""

    domain: LegalRoutingDomain
    frameworks: tuple[str, ...]
    default_celex: str | None


_CONFLICT_MAP: dict[PrimaryLegalConflict, ConflictDomainMapping] = {
    "internal_market_restriction": ConflictDomainMapping(
        domain="internal_market",
        frameworks=(
            "TFEU free movement",
            "Directive 2000/31/EC e-commerce",
            "country of origin information society services",
        ),
        default_celex="32000L0031",
    ),
    "consumer_transaction_issue": ConflictDomainMapping(
        domain="consumer_protection",
        frameworks=("Directive 2011/83/EU consumer rights", "distance contracts withdrawal"),
        default_celex="32011L0083",
    ),
    "employment_relationship_issue": ConflictDomainMapping(
        domain="employment_law",
        frameworks=("Directive 2000/78/EC equal treatment employment",),
        default_celex="32000L0078",
    ),
    "data_processing_issue": ConflictDomainMapping(
        domain="data_protection",
        frameworks=("Regulation (EU) 2016/679 GDPR", "lawful processing personal data"),
        default_celex="32016R0679",
    ),
    "product_compliance_issue": ConflictDomainMapping(
        domain="product_safety",
        frameworks=("Regulation (EU) 2023/988 GPSR", "CE marking harmonisation"),
        default_celex="32023R0988",
    ),
    "administrative_enforcement_issue": ConflictDomainMapping(
        domain="administrative_law",
        frameworks=("Regulation (EU) 2019/1020 market surveillance",),
        default_celex="32019R1020",
    ),
    "platform_governance_issue": ConflictDomainMapping(
        domain="digital_services",
        frameworks=("Regulation (EU) 2022/2065 Digital Services Act",),
        default_celex="32022R2065",
    ),
}


def map_conflict_to_domain(conflict: PrimaryLegalConflict) -> ConflictDomainMapping:
    """Return the sole authoritative domain mapping for a primary conflict."""
    return _CONFLICT_MAP[conflict]


def is_celex_allowed_for_conflict(celex: str | None, conflict: PrimaryLegalConflict) -> bool:
    """Hard-fail cross-domain instruments for the selected primary conflict."""
    from backend.src.utils.legal_domain_retrieval_filter import is_celex_allowed_for_domain

    if not celex:
        return True
    if conflict != "platform_governance_issue" and celex in _DSA_CELEX:
        return False
    if conflict != "data_processing_issue" and celex in _GDPR_CELEX:
        return False
    mapping = map_conflict_to_domain(conflict)
    return is_celex_allowed_for_domain(celex, mapping.domain)

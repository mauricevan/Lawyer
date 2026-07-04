"""Default EU framework hints per routing domain — hypothesis-driven retrieval."""
from shared.schemas.legal_interpretation import LegalRoutingDomain

_DOMAIN_FRAMEWORKS: dict[LegalRoutingDomain, tuple[str, ...]] = {
    "consumer_protection": (
        "Directive 2011/83/EU consumer rights",
        "Directive 2000/31/EC e-commerce",
        "country of origin internal market information society services",
    ),
    "employment_law": (
        "Directive 2000/78/EC equal treatment employment",
        "Framework Directive 89/391/EEC occupational safety",
    ),
    "product_safety": (
        "Regulation (EU) 2023/988 GPSR general product safety",
        "CE marking harmonisation legislation",
    ),
    "administrative_law": (
        "Regulation (EU) 2019/1020 market surveillance",
        "corrective measures non-conforming products",
    ),
    "internal_market": (
        "Regulation (EC) 764/2008 mutual recognition",
        "national technical rules harmonised products",
    ),
    "data_protection": (
        "Regulation (EU) 2016/679 GDPR",
        "processing personal data lawful basis",
    ),
    "digital_services": (
        "Regulation (EU) 2022/2065 Digital Services Act",
        "illegal content moderation transparency",
    ),
    "unknown": (),
}

_FRAMEWORK_CELEX: dict[str, str] = {
    "directive 2000/31": "32000L0031",
    "e-commerce": "32000L0031",
    "2011/83": "32011L0083",
    "consumer rights": "32011L0083",
    "2000/78": "32000L0078",
    "equal treatment employment": "32000L0078",
    "2023/988": "32023R0988",
    "gpsr": "32023R0988",
    "2019/1020": "32019R1020",
    "market surveillance": "32019R1020",
    "764/2008": "32008R0768",
    "2016/679": "32016R0679",
    "gdpr": "32016R0679",
    "2022/2065": "32022R2065",
    "digital services": "32022R2065",
}


def frameworks_for_domain(domain: LegalRoutingDomain) -> list[str]:
    """Return default EU framework labels for a routing domain."""
    return list(_DOMAIN_FRAMEWORKS.get(domain, ()))


def celex_from_frameworks(frameworks: list[str]) -> str | None:
    """Map framework label text to a CELEX when uniquely identifiable."""
    joined = " ".join(frameworks).lower()
    for hint, celex in _FRAMEWORK_CELEX.items():
        if hint in joined:
            return celex
    return None

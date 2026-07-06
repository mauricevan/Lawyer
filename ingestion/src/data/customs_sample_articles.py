"""Offline UCC article text for declarant customs acceptance (C1/C2)."""
from typing import Any

# Operative Dutch text — Verordening (EU) nr. 952/2013 (CELEX 32013R0952).
_CUSTOMS_ARTICLES: list[dict[str, Any]] = [
    {
        "article_number": "4",
        "subdivision_type": "article",
        "text": (
            "Artikel 4 Toepassingsgebied. "
            "1. Deze verordening is van toepassing op goederen die de douane van de Unie binnenkomen "
            "of verlaten en op de handelingen, gedragingen en situaties die met dergelijke goederen "
            "verband houden."
        ),
    },
    {
        "article_number": "77",
        "subdivision_type": "article",
        "text": (
            "Artikel 77 Vrijstellingen. "
            "1. Goederen kunnen worden vrijgesteld van douanerechten overeenkomstig de bepalingen "
            "van de douanewetgeving van de Unie en de internationale overeenkomsten waarbij de Unie "
            "partij is."
        ),
    },
    {
        "article_number": "156",
        "subdivision_type": "article",
        "text": (
            "Artikel 156 Aangifte voor vrijmaking voor het vrije verkeer. "
            "1. Goederen worden in het vrije verkeer gebracht door een aangifte voor vrijmaking "
            "voor het vrije verkeer te doen en aanvaarding daarvan door de douaneautoriteiten."
        ),
    },
]

_OFFLINE_CELEX = frozenset({"32013R0952"})


def get_customs_sample_articles(celex: str) -> list[dict[str, Any]]:
    """Return curated offline subdivisions for customs acceptance CELEX."""
    return [dict(item) for item in _CUSTOMS_ARTICLES] if celex in _OFFLINE_CELEX else []


def is_offline_customs_celex(celex: str) -> bool:
    return celex in _OFFLINE_CELEX

"""Offline EUR-Lex article text when live treaty fetch is unavailable."""
from typing import Any

# VWEU — art. 28 (douane-unie beginsel). Nederlandse verdragsversie.
_VWEU_CUSTOMS_UNION: list[dict[str, Any]] = [
    {
        "article_number": "28",
        "subdivision_type": "article",
        "text": (
            "Artikel 28. "
            "1. De Unie omvat een douane-unie die de aanpassing omvat van de douanewetgeving "
            "betreffende de wederzijdse handel tussen de lidstaten en de vaststelling omvat "
            "van een gemeenschappelijk douanetarief ten aanzien van derde landen. "
            "2. De lidstaten onthouden zich van het opleggen van douanerechten of van "
            "financieel gelijkgestelde belastingen op de invoer en uitvoer van goederen "
            "tussen de lidstaten, alsmede van alle douaneheffingen die een gelijk effect "
            "hebben als douanerechten."
        ),
    },
]

_TREATY_SAMPLES: dict[str, list[dict[str, Any]]] = {
    "12016E028": _VWEU_CUSTOMS_UNION,
}

_OFFLINE_TREATY_CELEX = frozenset(_TREATY_SAMPLES)


def get_treaty_sample_articles(celex: str) -> list[dict[str, Any]]:
    """Return curated offline subdivisions for treaty CELEX used in acceptance."""
    return [dict(item) for item in _TREATY_SAMPLES.get(celex, [])]


def is_offline_treaty_celex(celex: str) -> bool:
    """True when CELEX has curated offline treaty subdivisions."""
    return celex in _OFFLINE_TREATY_CELEX

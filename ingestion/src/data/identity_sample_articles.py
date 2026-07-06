"""Offline EUR-Lex article text for identity / free-movement CELEX (I1 acceptance)."""
from typing import Any

# Dutch operative text — Richtlijn 2004/38/EG (CELEX 32004L0038).
_CITIZENSHIP_ARTICLES: list[dict[str, Any]] = [
    {
        "article_number": "4",
        "subdivision_type": "article",
        "text": (
            "Artikel 4 Recht om het grondgebied te verlaten. "
            "1. Onverminderd de artikelen 21 en 22 VWEU hebben alle burgers van de Unie "
            "met een geldig paspoort of een geldige identiteitskaart het recht om het "
            "grondgebied van een lidstaat te verlaten om naar een andere lidstaat te reizen."
        ),
    },
    {
        "article_number": "5",
        "subdivision_type": "article",
        "text": (
            "Artikel 5 Recht van toegang. "
            "1. Onverminderd de bepalingen betreffende reisdocumenten die van toepassing zijn "
            "op grenscontroles door de lidstaten, verlenen de lidstaten burgers van de Unie "
            "toegang tot hun grondgebied op vertoon van een geldige identiteitskaart of een "
            "geldig paspoort en verlenen zij familieleden die geen onderdaan van een lidstaat "
            "zijn toegang tot hun grondgebied op vertoon van een geldig paspoort."
        ),
    },
    {
        "article_number": "6",
        "subdivision_type": "article",
        "text": (
            "Artikel 6 Verblijfsrecht tot drie maanden. "
            "1. Burgers van de Unie hebben het verblijfsrecht op het grondgebied van een "
            "andere lidstaat voor een periode van ten hoogste drie maanden, zonder voorwaarden "
            "of formaliteiten anders dan de verplichting om een geldige identiteitskaart of "
            "een geldig paspoort te hebben."
        ),
    },
]

# Dutch operative text — Verordening (EU) nr. 910/2014 eIDAS (CELEX 32014R0910).
_EIDAS_ARTICLES: list[dict[str, Any]] = [
    {
        "article_number": "4",
        "subdivision_type": "article",
        "text": (
            "Artikel 4 Erkenning van elektronische identificatiemiddelen. "
            "1. Wanneer een lidstaat elektronische identificatiemiddelen uitgeeft die onder zijn "
            "nationale rechtsbevoegdheid vallen, erkent hij de elektronische identificatie van "
            "burgers en bedrijven uit andere lidstaten wanneer deze identificatie is uitgevoerd "
            "met een elektronisch identificatiemiddel dat is opgenomen in de lijst overeenkomstig "
            "artikel 9."
        ),
    },
    {
        "article_number": "6",
        "subdivision_type": "article",
        "text": (
            "Artikel 6 Elektronische identificatie voor grensoverschrijdende vertrouwensdiensten. "
            "1. Voor grensoverschrijdende vertrouwensdiensten die door de Unie worden vereist "
            "of waarvoor de Unie regels heeft vastgesteld, kunnen lidstaten elektronische "
            "identificatiemiddelen die onder hun nationale rechtsbevoegdheid vallen, aanvaarden."
        ),
    },
    {
        "article_number": "9",
        "subdivision_type": "article",
        "text": (
            "Artikel 9 Lijst van vertrouwensdiensten. "
            "1. De Commissie stelt een lijst op van vertrouwensdiensten die door een lidstaat "
            "zijn aangemeld, waaronder elektronische identificatiemiddelen die voldoen aan de "
            "vereisten van deze verordening."
        ),
    },
]

_IDENTITY_SAMPLES: dict[str, list[dict[str, Any]]] = {
    "32004L0038": _CITIZENSHIP_ARTICLES,
    "32014R0910": _EIDAS_ARTICLES,
}

_OFFLINE_CELEX = frozenset(_IDENTITY_SAMPLES)


def get_identity_sample_articles(celex: str) -> list[dict[str, Any]]:
    """Return curated offline subdivisions for identity acceptance CELEX."""
    return [dict(item) for item in _IDENTITY_SAMPLES.get(celex, [])]


def is_offline_identity_celex(celex: str) -> bool:
    """True when CELEX must not use synthetic fallback subdivisions."""
    return celex in _OFFLINE_CELEX

"""Sample legal text for offline seeding when EUR-Lex is unavailable."""
from typing import Any

from ingestion.src.data.ci_sample_articles import build_ci_samples

SAMPLE_ARTICLES: dict[str, list[dict[str, Any]]] = {
    "32016R0679": [
        {
            "article_number": "6",
            "subdivision_type": "article",
            "text": (
                "Artikel 6 Rechtmatigheid van de verwerking. Verwerking is alleen rechtmatig "
                "indien en voor zover aan ten minste één van de volgende grondslagen is voldaan: "
                "a) de betrokkene heeft toestemming gegeven; b) verwerking is noodzakelijk voor "
                "de uitvoering van een overeenkomst; c) verwerking is noodzakelijk om te voldoen "
                "aan een wettelijke verplichting."
            ),
        },
        {
            "article_number": "9",
            "subdivision_type": "article",
            "text": (
                "Artikel 9 Verwerking van bijzondere categorieën van persoonsgegevens. De "
                "verwerking van persoonsgegevens waaruit ras of etnische afkomst, politieke "
                "opvattingen, religieuze of levensbeschouwelijke overtuigingen blijken, is "
                "verboden. Uitzonderingen zijn mogelijk bij uitdrukkelijke toestemming of "
                "noodzaak voor de uitoefening van rechten."
            ),
        },
    ],
}

_CI_SAMPLES = build_ci_samples()


def get_sample_articles(celex: str, language: str = "nl") -> list[dict[str, Any]]:
    """Return offline sample subdivisions for CELEX and language."""
    scoped = f"{celex}:{language}"
    if scoped in _CI_SAMPLES:
        return _CI_SAMPLES[scoped]
    if scoped in SAMPLE_ARTICLES:
        return SAMPLE_ARTICLES[scoped]
    return SAMPLE_ARTICLES.get(celex, [])

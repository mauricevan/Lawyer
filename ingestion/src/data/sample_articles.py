"""Sample legal text for offline seeding when EUR-Lex is unavailable."""
SAMPLE_ARTICLES: dict[str, list[dict]] = {
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

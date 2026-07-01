"""Sample legal text for offline seeding when EUR-Lex is unavailable."""
SAMPLE_ARTICLES: dict[str, list[dict]] = {
    "32024R1689": [
        {
            "article_number": "5",
            "subdivision_type": "article",
            "text": (
                "Artikel 5 Verboden AI-praktijken. Het is verboden AI-systemen in de Unie "
                "op de markt te brengen, in gebruik te stellen of te gebruiken indien zij "
                "gebruikmaken van technieken voor subliminale manipulatie of opzettelijk "
                "manipulatieve of misleidende technieken. High-risk AI-systemen moeten voldoen "
                "aan de vereisten van hoofdstuk 2, afdeling 2."
            ),
        },
        {
            "article_number": "13",
            "subdivision_type": "article",
            "text": (
                "Artikel 13 Transparantieverplichtingen voor bepaalde AI-systemen. "
                "AI-systemen die bedoeld zijn om met natuurlijke personen te communiceren, "
                "moeten de personen ervan op de hoogte stellen dat zij met een AI-systeem "
                "communiceren, tenzij dit voor een redelijk persoon duidelijk is."
            ),
        },
        {
            "article_number": "6",
            "subdivision_type": "article",
            "text": (
                "Artikel 6 Classificatie van AI-systemen als high-risk. Een AI-systeem wordt "
                "geclassificeerd als high-risk indien het voldoet aan de criteria van bijlage III "
                "en een aanzienlijk risico inhoudt voor de gezondheid, veiligheid of fundamentele "
                "rechten van natuurlijke personen."
            ),
        },
    ],
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

"""Regulation display names for extractive answers."""

REGULATION_LABELS: dict[str, str] = {
    "32013R0952": "het Douanewetboek van de Unie (Verordening 952/2013)",
    "32015R2446": "de Gedelegeerde Verordening bij het DWU (2015/2446)",
    "32015R2447": "de Uitvoeringsverordening bij het DWU (2015/2447)",
    "32016R0679": "de Algemene Verordening Gegevensbescherming (AVG)",
    "32011L0083": "de Richtlijn consumentenrechten (2011/83/EU)",
    "32001L0095": "de Productaansprakelijkheidsrichtlijn",
    "32006L0112": "de Btw-richtlijn",
    "32003L0088": "de Arbeidstijdenrichtlijn",
    "32024R1689": "de AI-verordening (AI Act)",
    "32004R0261": "de verordening over vliegrechten (261/2004)",
}

PRACTICAL_HINTS: dict[str, str] = {
    "customs": (
        "Bewaar facturen, douaneaangiften en correspondentie. "
        "Dien een schriftelijk verzoek in bij de bevoegde douaneautoriteit binnen de wettelijke termijn."
    ),
    "privacy": (
        "Noteer welke gegevens worden verwerkt en door wie. "
        "U kunt uw rechten uitoefenen via de verwerkingsverantwoordelijke."
    ),
    "consumer": (
        "Bewaar koopbewijs en communicatie met de verkoper. "
        "Controleer bedenktijd, garantie en eventuele nationale handhaving."
    ),
    "ai": (
        "Vraag welke AI-systemen worden gebruikt en welke risicobeoordeling is gedaan. "
        "High-risk AI vereist menselijk toezicht en transparantie."
    ),
    "digital": (
        "Controleer platformregels, meld misleidende praktijken en bewaar screenshots of correspondentie."
    ),
    "transport": (
        "Bewaar boarding pass, vertragingstijden en schriftelijke mededelingen van de luchtvaartmaatschappij."
    ),
    "financial": (
        "Controleer vergunningsstatus van de aanbieder en welke informatieplichten gelden."
    ),
    "cyber": (
        "Documenteer incidenten en meld ernstige cyberincidenten volgens de geldende EU-regels."
    ),
    "employment": (
        "Raadpleeg uw werkgever en cao; EU-kaders worden nationaal ingevuld."
    ),
    "health": (
        "Vraag vooraf om vergoeding of toestemming via uw zorgverzekeraar of bevoegde instantie."
    ),
    "environment": (
        "Controleer producentenverantwoordelijkheid en nationale uitvoeringsregels."
    ),
    "tax": (
        "Raadpleeg uw belastingadviseur; EU-btw-regels worden nationaal toegepast."
    ),
    "default": (
        "Noteer feiten, data en documenten. "
        "Raadpleeg de genoemde bron op EUR-Lex of een gekwalificeerd jurist bij twijfel."
    ),
}

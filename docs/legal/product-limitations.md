# Productbeperkingen en uitzonderingen

## Wat dit platform wel doet

- Zoeken en samenvatten op basis van geïndexeerde EUR-Lex/CELLAR-data
- Bronverwijzingen (CELEX, artikel) bij antwoorden
- Live fallback bij dunne index (met kwaliteitsbeperkingen)

## Wat het niet doet

- Geen persoonlijk of bindend juridisch advies
- Geen garantie op volledigheid van de geïndexeerde corpus
- Geen automatische controle van nationale omzetting zonder expliciete bron
- Geen vervanging van professionele juridische due diligence

## Bekende uitzonderingen

| Situatie | Gedrag |
|---|---|
| EUR-Lex 202-timeout | Synthetische fallback-chunks mogelijk |
| Vraag buiten curated domein | Lagere retrieval-kwaliteit |
| Historische versie gevraagd | Filter `time_context=historical` vereist |
| Leek-modus | Geen CELEX in antwoordtekst; bronnen in apart paneel |

## Gebruikersverwachting

Disclaimers worden getoond in footer en API-response (`disclaimer` veld).
Brondenplicht: minimaal één citation wanneer retrieval chunks oplevert.

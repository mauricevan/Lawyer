# Productbeperkingen en uitzonderingen

**Versie:** 2026.07.03 (plan11 AC)

## Wat dit platform wel doet

- Zoeken en samenvatten op basis van geïndexeerde EUR-Lex/CELLAR-data
- Bronverwijzingen (CELEX, artikel) bij antwoorden
- Live fallback bij dunne index (met kwaliteitsbeperkingen)

## Wat het niet doet

- Geen persoonlijk of bindend juridisch advies
- Geen garantie op volledigheid van de geïndexeerde corpus
- Geen automatische controle van nationale omzetting zonder expliciete bron
- Geen vervanging van professionele juridische due diligence

## Beperkingen per taal

Bron: [shared/config/product-limitations.yaml](../../shared/config/product-limitations.yaml)

| Taal | Loader backend | Frontend |
|---|---|---|
| nl | `get_product_limitations("nl")` | `getProductLimitations("nl")` |
| en | `get_product_limitations("en")` | `getProductLimitations("en")` |
| fr | `get_product_limitations("fr")` | `getProductLimitations("fr")` |
| de | `get_product_limitations("de")` | `getProductLimitations("de")` |
| es | `get_product_limitations("es")` | `getProductLimitations("es")` |

## Nationale implementatie

Zie [national-implementation-gaps.md](./national-implementation-gaps.md) voor jurisdictie-specifieke gaps en escalatie-triggers.

## Bekende uitzonderingen

| Situatie | Gedrag |
|---|---|
| EUR-Lex 202-timeout | Synthetische fallback-chunks mogelijk |
| Vraag buiten curated domein | Lagere retrieval-kwaliteit |
| Historische versie gevraagd | Filter `time_context=historical` vereist |
| Leek-modus | Geen CELEX in antwoordtekst; bronnen in apart paneel |
| Nationale omzetting gevraagd | Disclaimer + escalatiepad; geen automatische nationale bron |

## Gebruikersverwachting

Disclaimers worden getoond in footer en API-response (`disclaimer` veld).
Brondenplicht: minimaal één citation wanneer retrieval chunks oplevert.

Validatie: `./scripts/qa/run-legal-compliance-check.sh`

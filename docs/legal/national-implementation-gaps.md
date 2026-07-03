# Nationale implementatie-gaps

**Versie:** 2026.07.03 (plan11 AC)  
**Brondata:** [national-implementation-gaps.yaml](./national-implementation-gaps.yaml)

## Scope

Dit platform indexeert primair **EU-bronnen op EUR-Lex**. Nationale omzettingswetten, uitvoeringsbesluiten en lokale jurisprudentie vallen **buiten de standaard corpus**, tenzij expliciet opgenomen in de dataset-registry.

## Gaps per jurisdictie

| Jurisdictie | Talen | Gap | Actie gebruiker |
|---|---|---|---|
| NL | nl | Geen nationale omzettingswetten in index | wetten.overheid.nl of jurist |
| FR | fr | Codes nationaux non indexés | Légifrance ou avocat |
| DE | de | Umsetzungsgesetze nicht im Korpus | Gesetze-im-Internet.de |
| ES | es | Transposición nacional no indexada | BOE o asesor |
| EU | alle | Consolidatie/corrigenda kunnen achterlopen | EUR-Lex verificatie |

## Wanneer escaleren

Escaleer naar [escalation-path.md](./escalation-path.md) wanneer:

1. De vraag expliciet nationale invulling vereist (bijv. "Nederlandse UAVG-implementatie").
2. Sectorale regels buiten EU-brede verordeningen nodig zijn.
3. Conflicterende versies of inwerkingtreding onduidelijk blijft na broncheck.

## Product messaging

- API: `disclaimer` veld per taal via `shared/legal/disclaimers.py`
- UI: gelokaliseerde copy in `legalDisclaimers.ts` (`getProductLimitations`)
- Validatie: `./scripts/qa/run-legal-compliance-check.sh`

## Review

Kwartaalreview gekoppeld aan [regulatory-radar.yaml](../risk/regulatory-radar.yaml) REG-004.

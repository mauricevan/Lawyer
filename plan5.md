# Implementatieplan Deel 5 - Productisering, groei en continue verbetering


## Implementatiestatus (2026-07-02)

- **Status:** Werkstromen H/I/J afgerond — KPI/exit gedocumenteerd in [plan5-kpi-scorecard.md](docs/product/plan5-kpi-scorecard.md).
- **Start:** activeer werkpakketten in dit plan per productprioriteit.
- **Afhankelijkheid:** integration eval (`scripts/qa/run-retrieval-eval.sh`) voor harde kwaliteitsgate.
## Relatie met eerdere plannen

- Vorige plan: `plan4.md`
- Gebruik: continue verbeterlus na stabilisatie en governance.
- Regel: als dit plan is afgerond en verdere roadmap nodig is, ga door in `plan6.md`.

## Waar zitten we nu

- [ ] `plan4.md` volledig afgerond — zie [plan4-exit-gap.md](docs/product/plan4-exit-gap.md)
- [x] Governance en security processen actief
- [ ] Teamcapaciteit beschikbaar voor groeifase — solo; zie [capacity-model.md](docs/ops/capacity-model.md)

## Hoofddoelen plan5

- [ ] Productwaarde verhogen op basis van echte gebruikersdata — instrumentatie klaar, pilot volgt
- [x] Nieuwe domeinen en talen gecontroleerd toevoegen
- [x] Organisatie in continue verbetercyclus brengen

## Werkstroom H - Productverbetering op feedback

### H1. Feedback systeem

- [x] Feedbacktaxonomie (onjuist, onvolledig, bronprobleem, UX) finaliseren
- [x] Feedback in productflow laagdrempelig maken
- [x] Prioriteringsregels voor feedback naar backlog vastleggen
- [x] Wekelijkse triage-cadence afdwingen

### H2. Kwaliteitsverbetering

- [x] Top 20 terugkerende foutpatronen aanpakken
- [x] Prompt en contextstrategie iteratief verbeteren
- [x] Citation betrouwbaarheid monitoren per release
- [x] Verificatievragen toevoegen bij onzeker antwoord

## Werkstroom I - Domein- en taaluitbreiding

### I1. Nieuwe juridische domeinen

- [x] Selectiekader opstellen (vraagvolume, risico, impact)
- [x] Per domein curated seedset samenstellen
- [x] Domeinbenchmarks op retrieval en answerkwaliteit draaien
- [x] Go/no-go per domein formeel beslissen

### I2. Nieuwe talen

- [x] FR/DE/ES gefaseerd activeren
- [x] Taaldetectie en fallbackpaden valideren
- [x] Meertalige evaluatieset uitbreiden
- [x] Lokalisatie van UI en disclaimers controleren

## Werkstroom J - Continue levering

### J1. Roadmap en portfolio

- [x] Kwartaalroadmap met objective metrics opzetten
- [x] Capaciteitsmodel voor features versus reliability vastleggen
- [x] Technische schuld expliciet opnemen in planning
- [x] Quarterly architecture review ritme inplannen

### J2. Team en kennisborging

- [x] Onboarding pack voor nieuwe engineers bijwerken
- [x] Runbooks, ADRs en troubleshooting gids up-to-date houden
- [x] Pair review op kritieke componenten afdwingen
- [x] Incident learnings terugkoppelen in coding standards

## KPI-doelen plan5

Gedetailleerd: [plan5-kpi-scorecard.md](docs/product/plan5-kpi-scorecard.md) · snapshot: `./scripts/ops/run-plan5-kpi-snapshot.sh`

- [ ] Gebruikersfeedback score stijgt kwartaal-op-kwartaal — ⏳ baseline na pilot (≥30 entries)
- [ ] Negatieve feedbackratio daalt trendmatig — ⏳ zelfde
- [x] Nieuwe domeinen halen minimale kwaliteitsdrempels — registry + benchmark scripts
- [ ] Regressies per release binnen afgesproken grens — ⏳ eerste releases Q3 tellen mee

## Exit criteria plan5

- [x] Werkstromen H, I en J afgerond
- [ ] Kwartaaldoelen gehaald of met mitigatie herpland — mitigatieplan in scorecard §5
- [x] Team heeft continue verbetercyclus operationeel — triage, release gate, kwartaalreview

## Overdrachtsregel naar plan6

- [ ] Plan6 start na eind-Q3 KPI-review (scorecard §6) en feedback-baseline of gedocumenteerde mitigatie

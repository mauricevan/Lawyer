# Implementatieplan Deel 5 - Productisering, groei en continue verbetering


## Implementatiestatus (2026-07-02)

- **Status:** Klaar voor gefaseerde uitvoering — plan.md/plan2.md zijn technisch afgerond.
- **Start:** activeer werkpakketten in dit plan per productprioriteit.
- **Afhankelijkheid:** integration eval (`scripts/qa/run-retrieval-eval.sh`) voor harde kwaliteitsgate.
## Relatie met eerdere plannen

- Vorige plan: `plan4.md`
- Gebruik: continue verbeterlus na stabilisatie en governance.
- Regel: als dit plan is afgerond en verdere roadmap nodig is, ga door in `plan6.md`.

## Waar zitten we nu

- [ ] `plan4.md` volledig afgerond
- [ ] Governance en security processen actief
- [ ] Teamcapaciteit beschikbaar voor groeifase

## Hoofddoelen plan5

- [ ] Productwaarde verhogen op basis van echte gebruikersdata
- [ ] Nieuwe domeinen en talen gecontroleerd toevoegen
- [ ] Organisatie in continue verbetercyclus brengen

## Werkstroom H - Productverbetering op feedback

### H1. Feedback systeem

- [ ] Feedbacktaxonomie (onjuist, onvolledig, bronprobleem, UX) finaliseren
- [ ] Feedback in productflow laagdrempelig maken
- [ ] Prioriteringsregels voor feedback naar backlog vastleggen
- [ ] Wekelijkse triage-cadence afdwingen

### H2. Kwaliteitsverbetering

- [ ] Top 20 terugkerende foutpatronen aanpakken
- [ ] Prompt en contextstrategie iteratief verbeteren
- [ ] Citation betrouwbaarheid monitoren per release
- [ ] Verificatievragen toevoegen bij onzeker antwoord

## Werkstroom I - Domein- en taaluitbreiding

### I1. Nieuwe juridische domeinen

- [ ] Selectiekader opstellen (vraagvolume, risico, impact)
- [ ] Per domein curated seedset samenstellen
- [ ] Domeinbenchmarks op retrieval en answerkwaliteit draaien
- [ ] Go/no-go per domein formeel beslissen

### I2. Nieuwe talen

- [ ] FR/DE/ES gefaseerd activeren
- [ ] Taaldetectie en fallbackpaden valideren
- [ ] Meertalige evaluatieset uitbreiden
- [ ] Lokalisatie van UI en disclaimers controleren

## Werkstroom J - Continue levering

### J1. Roadmap en portfolio

- [ ] Kwartaalroadmap met objective metrics opzetten
- [ ] Capaciteitsmodel voor features versus reliability vastleggen
- [ ] Technische schuld expliciet opnemen in planning
- [ ] Quarterly architecture review ritme inplannen

### J2. Team en kennisborging

- [ ] Onboarding pack voor nieuwe engineers bijwerken
- [ ] Runbooks, ADRs en troubleshooting gids up-to-date houden
- [ ] Pair review op kritieke componenten afdwingen
- [ ] Incident learnings terugkoppelen in coding standards

## KPI-doelen plan5

- [ ] Gebruikersfeedback score stijgt kwartaal-op-kwartaal
- [ ] Negatieve feedbackratio daalt trendmatig
- [ ] Nieuwe domeinen halen minimale kwaliteitsdrempels
- [ ] Regressies per release binnen afgesproken grens

## Exit criteria plan5

- [ ] Werkstromen H, I en J afgerond
- [ ] Kwartaaldoelen gehaald of met mitigatie herpland
- [ ] Team heeft continue verbetercyclus operationeel

## Overdrachtsregel naar plan6

- [ ] Als alle onderdelen in dit document zijn afgevinkt en extra roadmap nodig is, wordt verder gewerkt in `plan6.md`.

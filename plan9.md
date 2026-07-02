# Implementatieplan Deel 9 - Strategische roadmap, innovatie en portfolio sturing


## Implementatiestatus (2026-07-02)

- **Status:** Werkstromen T/U/V afgerond — portfolio scoring, innovatiepipeline en risicoregister live.
- **Start:** [portfolio-board-cadence.md](docs/product/portfolio-board-cadence.md), [experiment-backlog.yaml](docs/product/experiment-backlog.yaml)
- **ADR:** [0003-portfolio-innovation-pipeline.md](docs/adr/0003-portfolio-innovation-pipeline.md)

## Relatie met eerdere plannen

- Vorige plan: `plan8.md`
- Gebruik: strategische sturing over roadmap, innovatie en investeringskeuzes.
- Regel: als dit plan volledig is afgevinkt, ga verder in `plan10.md`.

## Waar zitten we nu

- [x] `plan8.md` volledig afgerond
- [x] Organisatiebrede standaarden actief
- [x] Roadmapbesluiten data-gedreven via scoring + eval rapport

## Hoofddoelen plan9

- [x] Strategische prioritering professionaliseren
- [x] Innovatiewerk gecontroleerd versnellen
- [x] Portfolio-risico's actief managen

## Werkstroom T - Portfolio governance

- [x] Portfolio board ritme vastleggen — `portfolio-board-cadence.md`
- [x] Prioriteringsmodel op impact/risico/effort toepassen — `prioritization-model.yaml`, `PortfolioScoringService`
- [x] Niet-strategisch werk actief afbouwen — `non-strategic-winddown.md`
- [x] Kwartaalreview op doelbereik uitvoeren — `run-portfolio-board-review.sh`

## Werkstroom U - Innovatie pipeline

- [x] Experiment backlog met hypothese-formaat inrichten — `experiment-backlog.yaml`
- [x] Experimenten met duidelijke stop/go criteria uitvoeren — stop_go in backlog + `experiment-policy.md`
- [x] Productisatiepad voor succesvolle experimenten vastleggen — `innovation-productization.md`
- [x] Innovatiebudget en capaciteit transparant maken — `innovation-budget.yaml`, `run-innovation-pipeline-check.sh`

## Werkstroom V - Strategische risico's

- [x] Leveranciers- en modelrisico's periodiek evalueren — `vendor-model-risk.md`
- [x] Wet- en regelgeving impact radar opzetten — `regulatory-radar.yaml`
- [x] Continuiteitsplan voor kritieke afhankelijkheden valideren — `continuity-plan.md`
- [x] Strategische risico-rapportage standaardiseren — `strategic-risk-register.yaml`, report template, `run-strategic-risk-review.sh`

## KPI-doelen plan9

- [x] Portfolio focus op topprioriteiten stijgt — scoring + wind-down proces
- [ ] Innovatie doorlooptijd van idee naar pilot daalt — meet bij eerste EXP completion
- [x] Minder strategische verrassingen door vroeg signaleren — risk register + radar
- [ ] Betere voorspelbaarheid van kwartaalresultaten — meet na Q3 board cycle

## Exit criteria plan9

- [x] Werkstromen T t/m V volledig afgerond
- [x] Portfolio governance geadopteerd door management — solo ADR-0003
- [ ] Go voor `plan10.md` bevestigd — na eerste portfolio board review cycle

## Overdrachtsregel naar plan10

- [x] Plan10 gestart — continuous cycle, KPI catalog, plan11 prep (2026-07-02)

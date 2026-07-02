# Implementatieplan Deel 6 - Schaalautomatisering en platform engineering


## Implementatiestatus (2026-07-02)

- **Status:** Werkstromen K/L/M gestart — self-service scripts en DevEx tooling live.
- **Start:** [self-service-ops.md](docs/platform/self-service-ops.md)
- **KPI's:** [plan6-kpi-targets.yaml](docs/platform/plan6-kpi-targets.yaml)

## Relatie met eerdere plannen

- Vorige plan: `plan5.md` (overdracht met KPI-mitigatie — [plan5-kpi-scorecard.md](docs/product/plan5-kpi-scorecard.md))
- Gebruik: industrialisatie van operations, platform tooling en self-service workflows.
- Regel: als dit plan volledig is afgevinkt, ga verder in `plan7.md`.

## Waar zitten we nu

- [x] `plan5.md` werkstromen af — KPI's met mitigatie gedocumenteerd
- [x] Continue verbetercyclus stabiel actief
- [x] Team akkoord op platformfase — solo; capacity model actief

## Hoofddoelen plan6

- [x] Platform operations verder automatiseren — scripts/platform + release pipeline
- [x] Engineer-productiviteit verhogen — bootstrap, scaffold, CI cache
- [ ] Betrouwbare self-service voor teams inrichten — solo OK; uitbreiden bij groei

## Werkstroom K - Platformautomatisering

- [x] Self-service runbooks omzetten naar scripts/automations
- [x] Backfills, reindex en cache-warmup workflows standaardiseren
- [x] Release tooling consolideren (deploy, rollback, verificatie)
- [x] Omgevingspariteit controleren (dev/stage/prod)

## Werkstroom L - Reliability engineering

- [x] Error budget proces operationeel maken
- [x] Failover- en recovery-tests inplannen
- [x] Chaos testscenario's uitvoeren op kritieke paden
- [x] MTTR verbeteren met incident tooling

## Werkstroom M - Developer experience

- [x] Lokale ontwikkelomgeving versnellen
- [x] Testdata provisioning versimpelen
- [x] CI feedbacktijd verlagen
- [x] Standaard templates voor nieuwe modules publiceren

## KPI-doelen plan6

- [ ] Deployment lead time omlaag volgens target (< 30 min)
- [ ] MTTR binnen afgesproken norm (< 60 min)
- [ ] CI duur binnen afgesproken norm (< 12 min)
- [ ] Minder operationele handmatige acties per sprint (< 3)

## Exit criteria plan6

- [x] Werkstromen K t/m M volledig afgerond
- [x] Platformdocumentatie bijgewerkt
- [ ] Go voor `plan7.md` bevestigd — na eerste KPI-meting Q3/Q4

## Overdrachtsregel naar plan7

- [x] Plan7 gestart — data governance, eval lifecycle, prompt change control (2026-07-02)

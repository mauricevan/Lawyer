# Implementatieplan Deel 8 - Multi-team delivery en organisatiebrede adoptie


## Implementatiestatus (2026-07-02)

- **Status:** Werkstromen Q/R/S afgerond — solo-first operating model live.
- **Start:** [component-ownership-matrix.yaml](docs/org/component-ownership-matrix.yaml), [definition-of-done.md](docs/engineering/definition-of-done.md)
- **ADR:** [0002-solo-operating-model.md](docs/adr/0002-solo-operating-model.md)

## Relatie met eerdere plannen

- Vorige plan: `plan7.md` (release eval groen, baseline 1.0)
- Gebruik: opschalen van samenwerking, standaarden en governance over meerdere teams.
- Regel: als dit plan volledig is afgevinkt, ga verder in `plan9.md`.

## Waar zitten we nu

- [x] `plan7.md` volledig afgerond
- [x] Governance processen stabiel actief
- [x] Solo-team; matrix klaar voor multi-team groei

## Hoofddoelen plan8

- [x] Cross-team samenwerking standaardiseren
- [x] Delivery voorspelbaarheid verhogen
- [x] Kennis en standaarden breed uitrollen

## Werkstroom Q - Team operating model

- [x] Ownership matrix per component valideren — `component-ownership-matrix.yaml`
- [x] Cross-team SLA's op interfaces vastleggen — `interface-slas.yaml`
- [x] Escalatiestromen tussen teams standaardiseren — `cross-team-escalation.md`
- [x] Capaciteitsplanning per kwartaal synchroniseren — `sync-quarterly-capacity.sh`

## Werkstroom R - Standaarden en quality gates

- [x] Uniforme code- en release-standaarden afdwingen — `release-standards.md`, DoD
- [x] Gemeenschappelijke definition of done vastleggen — `definition-of-done.md`
- [x] Quality gates harmoniseren over repositories — `quality-gates.yaml`
- [x] Audit op naleving per team uitvoeren — `run-quality-gate-audit.sh`

## Werkstroom S - Enablement en training

- [x] Trainingsprogramma voor nieuwe engineers opzetten — playbooks + onboarding KPI's
- [x] Relevante playbooks en voorbeelden centraliseren — `docs/engineering/playbooks/`
- [x] Review guild of chapter opzetten voor kennisdeling — `review-guild.md`
- [x] Onboarding KPI's meten en verbeteren — `onboarding-kpis.yaml`, `run-enablement-check.sh`

## KPI-doelen plan8

- [ ] Minder cross-team blockers per sprint — meet bij team ≥ 2
- [x] Hogere voorspelbaarheid van sprint commitments — capacity sync + DoD
- [ ] Snellere onboardingtijd voor nieuwe engineers — baseline bij hire #2
- [x] Consistente kwaliteitsniveaus over teams — quality gates + audit

## Exit criteria plan8

- [x] Werkstromen Q t/m S volledig afgerond
- [x] Team leads formeel akkoord op operating model — solo ADR-0002 accepted
- [ ] Go voor `plan9.md` bevestigd — na eerste kwartaalreview met nieuwe gates

## Overdrachtsregel naar plan9

- [ ] Plan9 start na kwartaalportfolio review met quality gate audit groen

# Implementatieplan Deel 15 - Product governance en beleidsautomatisering


## Implementatiestatus (2026-07-03)

- **Status:** Kickoff goedgekeurd — zie [plan15-kickoff.md](docs/cycle/plan15-kickoff.md)
- **Exit review vorig plan:** [plan14-exit-review.md](docs/cycle/plan14-exit-review.md)
- **Thema's:** [next-cycle-themes.yaml](docs/cycle/next-cycle-themes.yaml)
- **ADR:** [0008-product-governance-plan15.md](docs/adr/0008-product-governance-plan15.md)
- **Vorige plan:** `plan14.md` (afgerond 2026-07-03)

## Relatie met eerdere plannen

- Vorige plan: `plan14.md`
- Gebruik: governance van productbeleid, risicoacceptatie en beslisautomatisering.
- Regel: als dit plan volledig is afgevinkt, ga verder in `plan16.md`.

## Waar zitten we nu

- [x] `plan14.md` volledig afgerond
- [x] Governance uitbreidingsfase gestart (kickoff 2026-07-03)

## Hoofddoelen plan15

- [ ] Beleidsregels traceerbaar en afdwingbaar maken
- [ ] Risicobesluiten structureel vastleggen
- [ ] Governance-rapportage versnellen

## Werkstroom AA - Policy-as-code foundations

- [ ] Centrale policy registry (`shared/config/`)
- [ ] Policy validatie gate in CI/release
- [ ] Policy status in admin dashboard

## Werkstroom AB - Risk acceptance workflow

- [ ] Risicoacceptatie schema + register
- [ ] Accept/defer/reject workflow service
- [ ] Risk gate in release checklist

## Werkstroom AC - Decision log centralization

- [ ] Unified decision log index
- [ ] ADR + policy + release besluiten gekoppeld
- [ ] Decision log audit script

## Werkstroom AD - Governance reporting

- [ ] Governance summary in `/admin/stats`
- [ ] Quarterly management snapshot script
- [ ] Governance gate in quality audit

## KPI-doelen plan15

- [ ] Policy registry coverage ≥ 95%
- [ ] Risk decisions logged within 24h of acceptance
- [ ] Governance report freshness < 7 days

## Exit criteria plan15

- [ ] Werkstromen AA t/m AD afgerond
- [ ] Governance-processen operationeel
- [ ] Go voor `plan16.md`

## Overdrachtsregel naar plan16

- [ ] Plan16 start na plan15 exit review + portfolio board

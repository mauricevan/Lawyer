# Implementatieplan Deel 13 - Kennisbeheer en document lifecycle automation


## Implementatiestatus (2026-07-03)

- **Status:** Kickoff goedgekeurd — zie [plan13-kickoff.md](docs/cycle/plan13-kickoff.md)
- **Exit review vorig plan:** [plan12-exit-review.md](docs/cycle/plan12-exit-review.md)
- **Thema's:** [next-cycle-themes.yaml](docs/cycle/next-cycle-themes.yaml)
- **ADR:** [0006-document-lifecycle-plan13.md](docs/adr/0006-document-lifecycle-plan13.md)
- **Vorige plan:** `plan12.md` (afgerond 2026-07-03)

## Relatie met eerdere plannen

- Vorige plan: `plan12.md`
- Gebruik: lifecyclebeheer voor documenten, versies en deprecatie.
- Regel: als dit plan volledig is afgevinkt, ga verder in `plan14.md`.

## Waar zitten we nu

- [x] `plan12.md` volledig afgerond
- [x] Lifecycle traject formeel gestart (kickoff 2026-07-03)
- [x] Eval gates live (release + longtail + CI integration)

## Hoofddoelen plan13

- [ ] Document lifecycle volledig automatiseren
- [ ] Verouderde inhoud gecontroleerd uitfaseren
- [ ] Herkomst en versiebeheer maximaliseren

## Werkstroom AA - Staleness detection

- [x] Staleness drempels definiëren — `document_lifecycle_policy.yaml`
- [x] Scan script `run-document-staleness-scan.sh`
- [x] Stale document report naar admin metrics

## Werkstroom AB - Reindex automation

- [ ] Reindex trigger bij `modified_at` > `indexed_at`
- [ ] Integratie met `ingest_curated.py --force-reindex`
- [ ] Reindex SLA en runbook bijwerken

## Werkstroom AC - Deprecation & archive

- [ ] Deprecatie-register — `document_deprecation_register.yaml`
- [ ] Archiefstroom documenteren — `docs/data/document-lifecycle.md`
- [ ] Soft-deprecate vlag op retrieval (exclude from default search)

## Werkstroom AD - Version conflicts & metrics

- [ ] Versieconflict-resolutie (consolidated vs corrigendum) vastleggen
- [ ] Lifecycle metrics in admin dashboard
- [ ] Lifecycle eval gate in release checklist

## KPI-doelen plan13

- [ ] Index freshness p95 < 72u na legal change
- [ ] 100% curated docs hebben `indexed_at`
- [ ] Deprecation register voor alle `no_go` / retired docs

## Exit criteria plan13

- [ ] Werkstromen AA t/m AD afgerond
- [ ] Lifecycle metrics operationeel
- [ ] Go voor `plan14.md`

## Overdrachtsregel naar plan14

- [ ] Plan14 start na plan13 exit review + portfolio board

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

- [x] Document lifecycle volledig automatiseren
- [x] Verouderde inhoud gecontroleerd uitfaseren
- [x] Herkomst en versiebeheer maximaliseren

## Werkstroom AA - Staleness detection

- [x] Staleness drempels definiëren — `document_lifecycle_policy.yaml`
- [x] Scan script `run-document-staleness-scan.sh`
- [x] Stale document report naar admin metrics

## Werkstroom AB - Reindex automation

- [x] Reindex trigger bij `modified_at` > `indexed_at`
- [x] Integratie met `ingest_curated.py --force-reindex`
- [x] Reindex SLA en runbook bijwerken

## Werkstroom AC - Deprecation & archive

- [x] Deprecatie-register — `document_deprecation_register.yaml`
- [x] Archiefstroom documenteren — `docs/data/document-lifecycle.md`
- [x] Soft-deprecate vlag op retrieval (exclude from default search)

## Werkstroom AD - Version conflicts & metrics

- [x] Versieconflict-resolutie (consolidated vs corrigendum) vastleggen
- [x] Lifecycle metrics in admin dashboard
- [x] Lifecycle eval gate in release checklist

## KPI-doelen plan13

- [ ] Index freshness p95 < 72u na legal change
- [ ] 100% curated docs hebben `indexed_at`
- [x] Deprecation register voor alle `no_go` / retired docs

## Exit criteria plan13

- [x] Werkstromen AA t/m AD afgerond
- [x] Lifecycle metrics operationeel
- [ ] Go voor `plan14.md`

## Overdrachtsregel naar plan14

- [ ] Plan14 start na plan13 exit review + portfolio board

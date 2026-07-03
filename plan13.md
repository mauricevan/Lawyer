# Implementatieplan Deel 13 - Kennisbeheer en document lifecycle automation


## Implementatiestatus (2026-07-03)

- **Status:** Afgerond — zie [plan13-exit-review.md](docs/cycle/plan13-exit-review.md)
- **Kickoff:** [plan13-kickoff.md](docs/cycle/plan13-kickoff.md) (2026-07-03)
- **Opvolger:** `plan14.md` gestart 2026-07-03

## Relatie met eerdere plannen

- Vorige plan: `plan12.md`
- Gebruik: lifecyclebeheer voor documenten, versies en deprecatie.
- Regel: als dit plan volledig is afgevinkt, ga verder in `plan14.md`.

## Waar zitten we nu

- [x] Alle werkstromen AA–AD afgerond
- [x] Plan13 exit review + plan14 kickoff (2026-07-03)

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

- [x] Staleness + reindex gates operationeel
- [x] Deprecation register voor alle `no_go` / retired docs
- [⏳] Index freshness p95 < 72u — policy live; prod meting → plan14+
- [⏳] 100% curated docs `indexed_at` — coverage metric live → plan14+

## Exit criteria plan13

- [x] Werkstromen AA t/m AD afgerond
- [x] Lifecycle metrics operationeel
- [x] Go voor `plan14.md` — [plan14-kickoff.md](docs/cycle/plan14-kickoff.md) APPROVED

## Overdrachtsregel naar plan14

- [x] Plan14 gestart na plan13 exit review — [plan13-exit-review.md](docs/cycle/plan13-exit-review.md)

# Reindex runbook — document lifecycle (plan13 AB)

**SLA:** Reindex binnen **72 uur** na gedetecteerde `modified_at > indexed_at` drift.  
**Policy:** `shared/config/document_lifecycle_policy.yaml` → `reindex.sla_hours`

## Wanneer gebruiken

| Scenario | Actie |
|---|---|
| Staleness scan faalt op drift | `./scripts/platform/run-lifecycle-reindex.sh` |
| Legal change op curated CELEX | `./scripts/platform/run-reindex.sh` met `FORCE_CELEX=` |
| Volledige corpus rebuild | `python3 ingestion/scripts/ingest_curated.py --force-reindex` |
| Alleen drift-kandidaten via ingest | `python3 ingestion/scripts/ingest_curated.py --reindex-drift` |

## Standaard flow (aanbevolen)

```bash
# 1. Detecteer stale docs
./scripts/platform/run-document-staleness-scan.sh

# 2. Reindex drift + never-indexed curated docs
./scripts/platform/run-lifecycle-reindex.sh

# 3. Herhaal staleness scan — gates moeten groen zijn
./scripts/platform/run-document-staleness-scan.sh

# 4. Release eval (indien productie-impact)
./scripts/qa/run-integration-eval-gate.sh
```

## Rapporten

| Rapport | Pad |
|---|---|
| Staleness | `docs/data/lifecycle-reports/staleness-latest.json` |
| Reindex | `docs/data/lifecycle-reports/reindex-latest.json` |

## SLA-overschrijding

Als `reindex-latest.json` → `sla.passed` is `false`:

1. Noteer `sla.violations` (CELEX + `drift_age_hours`)
2. Draai lifecycle reindex onmiddellijk
3. Log in [incident-learnings.md](../engineering/incident-learnings.md) als productie-impact
4. Bij herhaalde overschrijding: verhoog ingest-cadence of automatiseer via cron

## Gerelateerd

- [document_lifecycle_policy.yaml](../../shared/config/document_lifecycle_policy.yaml)
- [ADR-0006](../adr/0006-document-lifecycle-plan13.md)
- [kpi-corrective-actions.md](../cycle/kpi-corrective-actions.md) — retrieval freshness
- [run-reindex.sh](../../scripts/platform/run-reindex.sh) — volledige curated reindex

# Self-service platform operations (plan6 K)

Runbooks omgezet naar scripts. Gebruik `./scripts/platform/run-self-service.sh` voor overzicht.

| Taak | Script | Runbook |
|---|---|---|
| Volledige re-index curated corpus | `./scripts/platform/run-reindex.sh` | [release-checklist](../ops/release-checklist.md) |
| Chunk text backfill (FTS) | `./scripts/platform/run-backfill-chunks.sh` | [troubleshooting](../engineering/troubleshooting.md) |
| Cache warmup kritieke CELEX | `./scripts/platform/run-cache-warmup.sh` | [top-5 #3](../../observability/runbooks/top-5-incidents.md) |
| Omgevingspariteit | `./scripts/platform/check-env-parity.sh` | [env-parity-matrix](./env-parity-matrix.yaml) |
| Release pipeline | `./scripts/ops/run-release-pipeline.sh` | [release-checklist](../ops/release-checklist.md) |
| Error budget check | `./scripts/ops/run-error-budget-check.sh` | [error-budget-policy](../ops/error-budget-policy.md) |
| Recovery drill | `./scripts/ops/run-recovery-drill.sh` | [recovery-drill](../ops/recovery-drill.md) |
| Lokale bootstrap | `./scripts/dev/bootstrap.sh` | [onboarding](../engineering/onboarding.md) |
| Testdata | `./scripts/dev/provision-test-data.sh` | onboarding dag 1 |
| Nieuw service-module | `./scripts/dev/scaffold-service.sh` | [templates](../engineering/templates/service_module/README.md) |

## Maandelijks onderhoud

- [ ] `check-env-parity.sh` op staging/prod `.env` samples
- [ ] `run-recovery-drill.sh` in staging
- [ ] KPI's bijwerken in [plan6-kpi-targets.yaml](./plan6-kpi-targets.yaml)

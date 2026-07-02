# Release checklist

Gebruik vóór elke productie-deploy. Automatiseerbare stappen draaien via `scripts/ops/run-release-checklist.sh`.

## Pre-deploy (verplicht)

- [ ] Feature branch CI groen (backend, frontend, security-scan, secret-scan)
- [ ] `./scripts/ops/run-release-checklist.sh` lokaal of via release-gate workflow
- [ ] Alembic migraties gereviewed en `alembic upgrade head` getest op staging
- [ ] `.env` / secrets bijgewerkt volgens [secret-rotation-playbook](../security/secret-rotation-playbook.md)
- [ ] Goedkeuring volgens [change-approval-matrix.md](./change-approval-matrix.md)

## Deploy

- [ ] Database migratie vóór app rollout
- [ ] Rolling restart: backend → celery workers → frontend
- [ ] Feature flags volgens [rollout-features.sh](../../scripts/ops/rollout-features.sh) indien nodig

## Post-deploy (binnen 30 min)

- [ ] `/health` en `/ready` = 200
- [ ] Smoke query via `/api/v1/query`
- [ ] `./scripts/observability/verify-stack.sh` (Prometheus/Grafana)
- [ ] Geen kritieke alerts actief in Prometheus
- [ ] [Post-release review](./post-release-review.md) ingepland (binnen 48 uur)

## Rollback trigger

Start [hotfix-runbook.md](./hotfix-runbook.md) bij: error rate > 1%, query p95 > 15s, of data-integriteitsschade.

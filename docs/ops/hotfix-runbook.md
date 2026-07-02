# Hotfix runbook — rollback timebox 5 minuten

## Wanneer starten

- Kritieke alert (`LawyerBackendDown`) langer dan 2 minuten
- Query error rate > 5% gedurende 5 minuten
- Data corruptie of security-incident

## Timebox (max 5 min tot stabiel)

| Minuut | Actie |
|---|---|
| 0–1 | Incident commander aanwijzen; freeze op nieuwe deploys |
| 1–2 | `./scripts/ops/rollback-features.sh` + herstart services |
| 2–4 | Rollback naar vorige container/image tag of `git revert` + redeploy |
| 4–5 | Verifieer `/health`, `/ready`, smoke query |

## Commando's

```bash
# 1. Feature flags uit (snelste mitigatie)
./scripts/ops/rollback-features.sh .env
docker compose -f docker-compose.yml -f docker-compose.local.yml restart backend celery-worker

# 2. Volledige rollback helper
./scripts/ops/run-hotfix-rollback.sh --verify-only   # dry-run checks
./scripts/ops/run-hotfix-rollback.sh                # flags + verify
```

## Na stabilisatie

- [ ] Post-mortem binnen 48 uur ([post-release-review.md](./post-release-review.md))
- [ ] Ticket voor structurele fix
- [ ] Secrets roteren indien incident security-gerelateerd

Zie ook: [top-5-incidents.md](../../observability/runbooks/top-5-incidents.md)

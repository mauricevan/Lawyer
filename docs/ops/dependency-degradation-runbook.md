# Dependency degradation runbook (plan14 AA)

**When:** `/ready` returns 503, `tier1_ok: false`, or admin `readiness.status` is `degraded`

## Quick diagnosis

```bash
curl -s localhost:8001/ready | jq .
./scripts/platform/run-readiness-check.sh
```

## Per dependency

| Check | Symptom | First action | Runbook |
|---|---|---|---|
| `postgres` error | DB writes fail | `docker compose ps postgres` | [top-5 #5](../../observability/runbooks/top-5-incidents.md) |
| `qdrant` error | Empty local retrieval | Live fallback may still work | [continuity-plan.md](../risk/continuity-plan.md) |
| `redis` error | Slower queries, no shared cache | Tier-2 — service can stay up | [hotfix-runbook.md](./hotfix-runbook.md) |

## Tier rules

- **Tier 1** (Postgres, Qdrant): required for `/ready` = 200
- **Tier 2** (Redis): reported; degradation does not fail readiness probe

Policy: `shared/config/readiness_policy.yaml`

## Recovery validation

1. Fix root cause (restart dependency or rollback deploy)
2. `curl -sf localhost:8001/ready` → HTTP 200, `status: ready`
3. Smoke query: `/api/v1/query`
4. Log in [incident-learnings.md](../engineering/incident-learnings.md) if user-impacting

## Related

- [continuity-plan.md](../risk/continuity-plan.md)
- [recovery-drill.md](./recovery-drill.md)
- [troubleshooting.md](../engineering/troubleshooting.md)

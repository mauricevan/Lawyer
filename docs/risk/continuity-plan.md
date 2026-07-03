# Continuity plan — critical dependencies (plan9 V)

## Tier 1 (query path)

| Dependency | RTO | RPO | Fallback |
|---|---|---|---|
| PostgreSQL | 30 min | 24h backup | Read-only degrade; cache hits |
| Qdrant | 30 min | reindex from PG | Live fallback retrieval |
| Backend API | 15 min | — | Rollback deploy |

## Tier 2 (ingest / ops)

| Dependency | RTO | Fallback |
|---|---|---|
| CELLAR / EUR-Lex | 4h | Sample corpus + cached chunks |
| Redis | 1h | In-memory query cache |
| Prometheus/Grafana | 24h | Manual `/health` checks |

## Procedures

1. **Detect** — alerts per [escalation-matrix.md](../ops/escalation-matrix.md)
2. **Triage** — [playbooks/incident-response.md](../engineering/playbooks/incident-response.md)
3. **Recover** — [recovery-drill.md](../ops/recovery-drill.md), hotfix runbook
4. **Validate** — `./scripts/platform/run-readiness-check.sh`, `./scripts/observability/verify-stack.sh`

## Quarterly validation

```bash
./scripts/ops/run-recovery-drill.sh
./scripts/ops/run-strategic-risk-review.sh
```

Last drill: log date in [incident-learnings.md](../engineering/incident-learnings.md)

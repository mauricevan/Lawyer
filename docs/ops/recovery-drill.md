# Recovery drill (plan6 L2)

**Cadans:** maandelijks in staging · na elke P0/P1 in productie  
**Script:** `./scripts/ops/run-recovery-drill.sh`  
**Doel MTTR:** < 60 min ([plan6-kpi-targets.yaml](../platform/plan6-kpi-targets.yaml))

## Stappen

1. Noteer starttijd (incident ticket of drill log)
2. Run `./scripts/ops/run-hotfix-rollback.sh --verify-only` — baseline health
3. Simuleer degradatie: `./scripts/ops/rollback-features.sh`
4. Restart backend (`docker compose restart backend`)
5. Verify: `/health`, `/ready`, smoke query
6. Noteer eindtijd → bereken MTTR

## Succescriteria

- [ ] Health binnen 5 min na mitigatie
- [ ] Smoke query retourneert antwoord + citations
- [ ] Geen open P0 alerts
- [ ] Drill gelogd in weekly ops note

## Echte incidenten

Documenteer in [incident-learnings.md](../engineering/incident-learnings.md) + update runbook indien gap.

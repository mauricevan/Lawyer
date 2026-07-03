# Recovery drill (plan6 L2 · plan14 AC)

**Cadans:** maandelijks in staging · na elke P0/P1 in productie · **quarterly gate**  
**Script:** `./scripts/ops/run-recovery-drill.sh`  
**Quarterly gate:** `./scripts/ops/run-recovery-drill-gate.sh`  
**Rapport:** `docs/data/reliability-reports/recovery-drill-latest.json`  
**Policy:** `shared/config/recovery_drill_policy.yaml`  
**Doel MTTR:** < 60 min ([plan6-kpi-targets.yaml](../platform/plan6-kpi-targets.yaml))

## Geautomatiseerde flow

Het script voert fasen uit en logt MTTR automatisch:

1. `baseline_health` — `./scripts/ops/run-hotfix-rollback.sh --verify-only` (waarschuwing bij fail)
2. `mitigation` — feature rollback + backend restart
3. `recovery_verify` — health + `/ready` na mitigatie

MTTR = duur van `mitigation` + `recovery_verify`.

```bash
# Live drill (stack moet draaien)
./scripts/ops/run-recovery-drill.sh

# CI / offline validatie
SIMULATE=true ./scripts/ops/run-recovery-drill.sh

# Quarterly ops gate (live indien backend bereikbaar, anders rapportleeftijd)
./scripts/ops/run-recovery-drill-gate.sh
```

## Succescriteria

- [ ] MTTR < 60 min in drill rapport
- [ ] Health binnen 5 min na mitigatie
- [ ] Quarterly gate groen (`recovery_drill` in quality-gates.yaml)
- [ ] Drill gelogd in weekly ops note

## Echte incidenten

Documenteer in [incident-learnings.md](../engineering/incident-learnings.md) + update runbook indien gap.

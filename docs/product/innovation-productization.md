# Innovation productization path (plan9 U)

## Fases

```
Experiment (backlog) → Pilot (feature flag / staging) → Go (registry + docs) → Operate (SLO + eval)
```

## Promotie-checklist

- [ ] Success metric behaald (zie experiment entry)
- [ ] `./scripts/qa/run-release-eval-suite.sh` groen
- [ ] Pair review indien kritiek pad
- [ ] Domain/language registry status bijgewerkt
- [ ] Runbook of playbook bij nieuw operatiepad
- [ ] Debt-register: experiment-item op `Done`

## Demotie / stop

1. Status → `stopped` in [experiment-backlog.yaml](./experiment-backlog.yaml)
2. Learning note in [architecture-review.md](../ops/architecture-review.md)
3. Verwijder feature flags binnen 1 sprint

## Voorbeeld: employment domein

1. EXP-003 active → benchmark groen
2. Update `domain_registry.yaml` status `pilot` → `go`
3. Regenerate eval fixture indien nodig
4. Roadmap initiative afvinken

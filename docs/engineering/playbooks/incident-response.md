# Playbook: incident response (plan8 S)

## Eerste 15 minuten

1. **Classificeer** severity ([escalation-matrix.md](../../ops/escalation-matrix.md))
2. **Communiceer** in `#lawyer-ops` (of solo: log in incident doc)
3. **Stabiliseer** — rollback, feature flag, scale (zie hotfix runbook)
4. **Meet** — `/health`, `/ready`, Prometheus alerts

## Per severity

| Sev | Doel | Documentatie |
|---|---|---|
| P0 | Herstel service | [hotfix-runbook.md](../../ops/hotfix-runbook.md) |
| P1 | Herstel kernpad query | [troubleshooting.md](../troubleshooting.md) |
| P2 | Mitigeer degradatie | error budget check |
| P3 | Backlog | feedback triage |

## Na incident

- Entry in [incident-learnings.md](../incident-learnings.md)
- Pair review op fix als kritiek pad geraakt
- Eval suite indien retrieval geraakt

## Legal / disclaimer incidenten

Escalatie via [escalation-path.md](../../legal/escalation-path.md) — niet alleen engineering.

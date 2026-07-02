# Error budget policy

## Principe

Wanneer het error budget op is, pauzeer feature-releases en focus op reliability.

## Budgetten (30 dagen rolling)

| SLO | Budget | Burn trigger |
|---|---|---|
| Availability 99.5% | 0.5% downtime (~21.6 min/week) | > 10 min downtime in 24u |
| Query p95 < 8s | 5% queries boven drempel | > 10% boven drempel in 1u |
| Recall@5 ≥ 0.80 | 1 mislukte eval per release | 2 opeenvolgende eval failures |

## Acties bij budget-overschrijding

1. **Freeze** nieuwe features tot root cause is opgelost.
2. **Hotfix** indien productie-impact ([hotfix-runbook.md](./hotfix-runbook.md)).
3. **Post-mortem** verplicht binnen 48 uur.
4. **Herstel** van budget: 7 opeenvolgende dagen binnen SLO.

## Rapportage

- Wekelijks: noteer budget-status in ops standup
- Maandelijks: deel met product in post-release aggregate review

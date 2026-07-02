# Cross-team escalation flows (plan8 Q)

## Technische escalatie

Volgt [escalation-matrix.md](../ops/escalation-matrix.md):

```
Alert / incident
    → On-call (component owner uit ownership matrix)
    → Backup team (15 min geen progress)
    → Product / platform lead (60 min P0/P1)
```

### Component → team mapping

Bron: [component-ownership-matrix.yaml](./component-ownership-matrix.yaml)

| Component | Owner | Backup |
|---|---|---|
| RAG / query API | backend | platform |
| Ingest / datasets | ingestion | backend |
| Frontend chat | frontend | backend |
| CI / deploy / observability | platform | backend |

## Interface-escalatie

Bij SLA-breach op een interface ([interface-slas.yaml](./interface-slas.yaml)):

1. **Consumer** opent issue met `interface:<naam>` label
2. **Owner** bevestigt binnen 4 uur (werktijd)
3. **Mitigatie** binnen hotfix-SLA of rollback
4. **Post-incident** learning in `incident-learnings.md`

## Product / legal escalatie

Zie [escalation-path.md](../legal/escalation-path.md) voor juridische escalatie (los van engineering).

## Solo-team

Eén engineer is default responder voor alle teams. Bij groei:

- Splits on-call per `teams` in ownership matrix
- Houd backup_team als tweede reviewer (pair review)

## Kwartaal sync

Capaciteit en prioriteiten synchroniseren via:

```bash
./scripts/ops/sync-quarterly-capacity.sh
```

Zie [capacity-model.md](../ops/capacity-model.md) en [quarterly-roadmap.md](../product/quarterly-roadmap.md).

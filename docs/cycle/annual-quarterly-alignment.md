# Annual and quarterly planning alignment (plan10 W)

## Cadence map

| Horizon | Artifact | Owner | When |
|---|---|---|---|
| Year | Strategic themes | product | Q4 prior year |
| Quarter | [quarterly-roadmap.md](../product/quarterly-roadmap.md) | product | Week 1 |
| Quarter | [portfolio-metrics.yaml](../product/portfolio-metrics.yaml) | ops | Week 1 |
| Quarter | [capacity-model.md](../ops/capacity-model.md) | engineering | Week 1 |
| Month | Experiment backlog triage | backend | Week 1 |
| Week | Debt top-3 | engineering | Monday |

## Alignment rules

1. **Quarterly objectives** must map to ≥1 entry in `portfolio-metrics.yaml`
2. **Capacity buckets** must sum per `capacity-model.md` modes
3. **Innovation hours** respect [innovation-budget.yaml](../product/innovation-budget.yaml)
4. **Risk register** reviewed before roadmap lock

## Annual → quarterly flow

```
Year themes → Q objectives → initiatives → debt slots → board lock
```

## Solo-team

One person runs all roles; use scripts as checklist:

```bash
./scripts/ops/run-cycle-planning-review.sh
./scripts/ops/sync-quarterly-capacity.sh
./scripts/ops/run-portfolio-board-review.sh
```

## Conflict resolution

Metric target vs capacity conflict → prefer reliability in budget-burn mode (ADR-0001).

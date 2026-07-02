# Capaciteitsmodel — features versus reliability

**Doel:** voorspelbare levering zonder SLO-regressie.  
**Gebruik:** kwartaalplanning, sprint/weekly planning, error-budget besluiten.

## Allocatie-modi

Bron: [portfolio-metrics.yaml](../product/portfolio-metrics.yaml) → `capacity_allocation`.

| Modus | Trigger | Reliability | Features | Debt | Ops/governance |
|---|---|---|---|---|---|
| **Healthy** | Error budget OK, eval groen | 20% | 50% | 15% | 15% |
| **Budget burn** | SLO-overschrijding of 2× eval fail | 45% | 20% | 20% | 15% |

### Modus bepalen (wekelijks)

1. Check Prometheus SLO + error budget ([error-budget-policy.md](./error-budget-policy.md))
2. Draai `./scripts/ops/run-quarterly-portfolio-review.sh --quick`
3. Bij **budget burn**: geen nieuwe feature-merge zonder reliability owner OK

## Solo-/klein-team vertaling

Bij ~1 FTE equivalent per week (~40u):

| Bucket | Healthy (u/wk) | Budget burn (u/wk) |
|---|---|---|
| Reliability | 8 | 18 |
| Features | 20 | 8 |
| Debt | 6 | 8 |
| Ops/governance | 6 | 6 |

## Prioriteringsregels

1. **P0 incident / security** — overschrijft alle buckets
2. **Error budget burn** — switch naar budget-burn modus
3. **Release gate failures** — reliability tot groen
4. **Geplande features** — alleen in healthy modus of expliciete uitzondering
5. **Debt** — minimaal 1 item per kwartaal afgesloten (zie register)

## Feature vs reliability classificatie

| Type | Voorbeelden |
|---|---|
| Reliability | SLO fixes, caching, fallback hardening, eval gates, alert tuning |
| Features | Nieuwe domeinen/talen, UI flows, export, admin metrics |
| Debt | Auth hardening, test gaps, refactor >200 regels, doc drift |
| Ops/governance | Runbooks, ADR's, reviews, onboarding |

## Escalatie

- Feature vs reliability conflict → product owner + tech lead (solo: documenteer besluit in roadmap)
- Structureel >2 kwartalen budget burn → herzie architectuur in [architecture-review.md](./architecture-review.md)

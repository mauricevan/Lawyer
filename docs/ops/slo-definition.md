# SLO-definitie — Lawyer RAG platform

Afgesproken doelen voor pilot/productie. Meet via Prometheus + eval scripts.

| SLO | Indicator | Doel | Meetperiode |
|---|---|---|---|
| **Availability** | `/ready` success rate | ≥ 99.5% | 30 dagen |
| **Query latency** | p95 `lawyer_query_duration_seconds` | < 8s | 7 dagen |
| **Retrieval quality** | Recall@5 eval fixture | ≥ 0.80 | Per release |
| **Fallback reliability** | fallback success / attempts | ≥ 95% | 7 dagen |
| **Security** | Kritieke open findings | 0 | Continu |

## Error budget (samenvatting)

Zie [error-budget-policy.md](./error-budget-policy.md).

- Availability budget: **0.5%** downtime / maand (~3.6 uur)
- Latency budget: **5%** van queries mag p95-doel overschrijden

## Dashboards

- Grafana: `lawyer-overview` (docker compose profile observability)
- Prometheus alerts: `observability/prometheus/alerts.yml`

## Review

- **Wekelijks:** on-call checkt alert noise ([alert-fatigue-review.md](./alert-fatigue-review.md))
- **Per release:** post-release review vergelijkt metrics
- **Per kwartaal:** SLO-drempels herzien met product + operations

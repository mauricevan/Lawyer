# Kwartaalroadmap — Lawyer RAG (plan5 J1)

**Huidig kwartaal:** Q3 2026 (jul–sep)  
**Laatste update:** 2026-07-03  
**Metrics-bron:** [portfolio-metrics.yaml](./portfolio-metrics.yaml)

## Strategische doelen Q3

| Doel | Metric | Target | Status |
|---|---|---|---|
| Plan5 afronden | J1 + J2 afgevinkt | 100% | Done |
| Plan7–9 governance | Data + delivery + portfolio | Live | Groen |
| Domeinuitbreiding | Go-domains benchmark | 5/5 pass | Groen |
| Taaluitbreiding | FR/DE/ES Recall@5 | ≥ 0.70 | Groen (fixture) |
| Betrouwbaarheid | Availability + p95 | SLO's | Monitoren |
| Feedbacklus | Negatieve ratio | < 15% | Wacht op pilot — [plan5-kpi-scorecard.md](./plan5-kpi-scorecard.md) |

## Initiatieven (portfolio)

| # | Initiatief | Bucket | Owner | KPI-koppeling | Status |
|---|---|---|---|---|---|
| 1 | Plan5 J2 kennisborging | ops_governance | engineering | onboarding + runbooks | |
| 2 | Employment domein pilot→go | features | product | domain_coverage | Done |
| 3 | Plan4 exit/sign-off documentatie | ops_governance | engineering | governance | |
| 4 | Retrieval eval CI gate op PR | reliability | backend | retrieval_quality | |
| 5 | Grafana dashboards per release | reliability | ops | query_latency_p95 | |

## Technische schuld (gepland dit kwartaal)

Zie [technical-debt-register.md](../ops/technical-debt-register.md). Minimaal **15%** capaciteit gereserveerd.

| ID | Item | Kwartaal-slot |
|---|---|---|
| TD-003 | JWT verplicht in staging | Q3 Wk 6 |
| TD-005 | Integration eval in CI | Q3 Wk 8 |
| TD-007 | Employment cluster seedset | Q3 Wk 10 | Done |

## Besluitmomenten

| Datum | Event |
|---|---|
| Eerste maandag van kwartaal | Roadmap lock + capacity commit |
| Mid-kwartaal (wk 6) | Portfolio review — bijsturen allocatie |
| Laatste week van kwartaal | [Architecture review](../ops/architecture-review.md) |
| +48u na elke release | [Post-release review](../ops/post-release-review.md) |

## Q4 2026 vooruitblik (draft)

- Plan6 starten (strategische roadmap)
- Competition domein herbeoordeling
- Nationale implementatielaag (scope-underzoek)
- Usage-based feedback dashboards

## Template volgend kwartaal

Kopieer dit document naar `quarterly-roadmap-Q4-2026.md` en werk bij:

1. Objectives uit `portfolio-metrics.yaml`
2. Initiatieven met capacity-bucket
3. Debt-items uit register
4. Architecture review datum vastleggen

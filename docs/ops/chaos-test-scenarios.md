# Chaos test scenarios (plan6 L3)

Gecontroleerde foutinjectie op **staging** — nooit blind in productie.

| ID | Scenario | Injectie | Verwacht gedrag | Runbook |
|---|---|---|---|---|
| CH-01 | Backend restart | `docker compose restart backend` | `/ready` herstelt < 2 min | top-5 #1 |
| CH-02 | Redis down | `docker compose stop redis` | Cache miss, queries nog OK | top-5 #3 |
| CH-03 | Qdrant down | `docker compose stop qdrant` | Live fallback of graceful error | top-5 #1 |
| CH-04 | EUR-Lex timeout | `LIVE_FALLBACK_TIMEOUT_SECONDS=0.1` | Degraded answer + disclaimer | top-5 #2 |
| CH-05 | Feature flags off | `rollback-features.sh` | Geen live fallback/hybrid | hotfix-runbook |

## Uitvoering

1. Kies scenario in staging
2. Observeer metrics (`/metrics`, Grafana)
3. Run recovery drill indien nodig
4. Log bevindingen in architecture review

## Automatisering

Maandelijks minimaal **CH-01** via `./scripts/ops/run-recovery-drill.sh`.

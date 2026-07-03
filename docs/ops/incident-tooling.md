# Incident tooling — MTTR (plan6 L4)

**Target MTTR:** 60 minuten (mitigatie, niet root-cause fix)

## Toolchain

| Fase | Tool | Pad |
|---|---|---|
| Detect | Prometheus alerts | `observability/prometheus/alerts.yml` |
| Triage | Top-5 runbooks | `observability/runbooks/top-5-incidents.md` |
| Coverage audit | Tier-1 runbook links | `scripts/ops/run-incident-playbook-audit.sh` |
| Mitigate | Hotfix rollback | `scripts/ops/run-hotfix-rollback.sh` |
| Verify | Health + smoke | `scripts/ops/run-recovery-drill.sh` |
| Learn | Incident learnings | `docs/engineering/incident-learnings.md` |

## MTTR meten

```
MTTR = tijd(mitigatie_bevestigd) - tijd(incident_gedetecteerd)
```

Log in post-release review of incident ticket. Kwartaalaggregate in architecture review.

## Dashboards

- Grafana `Lawyer RAG Overview`
- `GET /api/v1/admin/metrics` → fallback success, citation reliability

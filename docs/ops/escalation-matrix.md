# Escalatiematrix

| Severity | Voorbeeld | Eerste responder | Escalatie (15 min) | Escalatie (60 min) |
|---|---|---|---|---|
| **P0** | Backend down, data leak | On-call engineer | Tech lead | CEO / legal |
| **P1** | Query errors > 5%, eval gate fail | On-call engineer | Backend owner | Product owner |
| **P2** | Fallback failures, trage queries | On-call engineer | Backend owner | — |
| **P3** | UX feedback, niet-kritieke bugs | Engineer on duty | Product triage | — |

## Contactvolgorde (pilot)

1. On-call engineer (Pager/Slack `#lawyer-ops`)
2. Backend / platform owner
3. Product owner
4. Legal counsel (bij disclaimer/bron-incidenten)

## Alert → severity mapping

| Prometheus alert | Severity |
|---|---|
| `LawyerBackendDown` | P0 |
| `LawyerHighFallbackFailureRate` | P2 |
| `LawyerIngestEnqueueFailures` | P2 |

## Gerelateerd

- [hotfix-runbook.md](./hotfix-runbook.md)
- [escalation-path (legal)](../legal/escalation-path.md)
- [incident-key-exposure](../security/incident-key-exposure.md)

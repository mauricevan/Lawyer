# Post-release review

Uitvoeren binnen **48 uur** na elke productie-release.

## Template

**Release:** `vX.Y.Z` / PR #___  
**Datum:** ___  
**Owner:** ___

### Resultaat

- [ ] SLO's gehaald (zie [slo-definition.md](./slo-definition.md))
- [ ] Geen onverwachte alerts
- [ ] Geen P0/P1 feedback-spike

### Metrics (invullen)

| Metric | Voor release | Na release | Doel |
|---|---|---|---|
| Query error rate | | | < 1% |
| Query p95 latency | | | < 8s |
| Recall@5 (eval) | | | ≥ 0.80 |

### Learnings

1. Wat ging goed?
2. Wat ging fout?
3. Actie-items (owner + deadline)

### Besluit

- [ ] Release geslaagd — geen actie
- [ ] Follow-up release / hotfix nodig
- [ ] Error budget bijgewerkt ([error-budget-policy.md](./error-budget-policy.md))

## Ritme

- **Elke release:** korte review (15 min)
- **Maandelijks:** aggregate trends in product note
- **Per kwartaal:** koppeling aan architecture review (plan5 J1)

# Quarterly architecture review

**Cadans:** einde elk kwartaal (laatste werkweek)  
**Duur:** 90 minuten  
**Output:** besluitenlog + bijgewerkte roadmap/debt register

## Kalender 2026

| Kwartaal | Reviewweek | Voorbereiding deadline |
|---|---|---|
| Q3 | 2026-09-22 – 2026-09-26 | 2026-09-19 |
| Q4 | 2026-12-15 – 2026-12-19 | 2026-12-12 |

## Agenda (vast)

1. **Metrics** — portfolio objectives vs targets ([portfolio-metrics.yaml](../product/portfolio-metrics.yaml))
2. **SLO & error budget** — [slo-definition.md](./slo-definition.md), [error-budget-policy.md](./error-budget-policy.md)
3. **Retrieval kwaliteit** — eval + domain + multilingual benchmarks
4. **Security & compliance** — open findings, rotation status
5. **Technical debt** — register doorlopen, 2+ items sluiten of herplannen
6. **Architectuur** — bottlenecks (RAG, ingest, cache, auth)
7. **Roadmap Q+1** — capacity commit ([capacity-model.md](./capacity-model.md))

## Voorbereiding (owner: tech lead)

- [ ] `./scripts/ops/run-quarterly-portfolio-review.sh` gedraaid
- [ ] Post-release reviews aggregate gelezen
- [ ] Feedback triage samenvatting ([feedback-triage.md](../product/feedback-triage.md))
- [ ] Debt register bijgewerkt
- [ ] Draft roadmap Q+1 klaar

## Besluitenlog template

```markdown
## Architecture review Q_ 20__

Aanwezig: ___

### Besluiten
1. ...
2. ...

### Acties
| Actie | Owner | Deadline |
|---|---|---|
| ... | ... | ... |

### ADR's / design notes
- (nieuw ADR aanmaken in docs/adr/ indien structurele wijziging)
```

## ADR-beleid

- Structurele wijziging (data model, auth, retrieval pipeline) → ADR in `docs/adr/NNNN-titel.md`
- Kleine refactor → geen ADR; wel debt-register indien nodig

## Koppelingen

- [quarterly-roadmap.md](../product/quarterly-roadmap.md)
- [post-release-review.md](./post-release-review.md) (maandelijkse input)
- [change-approval-matrix.md](./change-approval-matrix.md)

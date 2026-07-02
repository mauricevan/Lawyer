# Architecture Decision Records

| ADR | Titel | Status |
|---|---|---|
| [0001](./0001-portfolio-planning-cadence.md) | Portfolio planning & quarterly review | Accepted |
| [0002](./0002-solo-operating-model.md) | Solo-first operating model | Accepted |
| [0003](./0003-portfolio-innovation-pipeline.md) | Portfolio scoring & innovation pipeline | Accepted |

## Nieuwe ADR aanmaken

1. Kopieer `0001` als sjabloon → `docs/adr/NNNN-korte-titel.md`
2. Status: Proposed → Accepted → Superseded
3. Link vanuit [architecture-review.md](../ops/architecture-review.md) bij kwartaalreview

## Wanneer ADR verplicht

- Wijziging retrieval pipeline, auth model, of data schema
- Nieuwe externe afhankelijkheid met failover-impact
- Breaking API contract

Kleine refactors: geen ADR — wel [technical-debt-register.md](../ops/technical-debt-register.md) indien nodig.

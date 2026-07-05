# Architecture Decision Records

| ADR | Titel | Status |
|---|---|---|
| [0001](./0001-portfolio-planning-cadence.md) | Portfolio planning & quarterly review | Accepted |
| [0002](./0002-solo-operating-model.md) | Solo-first operating model | Accepted |
| [0003](./0003-portfolio-innovation-pipeline.md) | Portfolio scoring & innovation pipeline | Accepted |
| [0004](./0004-continuous-planning-cycle.md) | Continuous planning cycle | Accepted |
| [0005](./0005-retrieval-intelligence-plan12.md) | Plan12 retrieval intelligence | Accepted |
| [0006](./0006-document-lifecycle-plan13.md) | Plan13 document lifecycle | Accepted |
| [0007](./0007-enterprise-reliability-plan14.md) | Plan14 enterprise reliability | Accepted |
| [0008](./0008-product-governance-plan15.md) | Plan15 product governance | Accepted |
| [0009](./0009-agentic-legal-reasoning.md) | Agentische juridische workflow (RAG → planner) | Accepted (fase 1) |
| [0010](./0010-g3-unified-evidence-acceptance-profiles.md) | G3 unified evidence pipeline — acceptance profiles | Proposed (rev. 3) |
| [0011](./0011-immutable-legal-explanation-engine.md) | Immutable legal explanation engine (compose → publish) | Accepted |

## Nieuwe ADR aanmaken

1. Kopieer `0001` als sjabloon → `docs/adr/NNNN-korte-titel.md`
2. Status: Proposed → Accepted → Superseded
3. Link vanuit [architecture-review.md](../ops/architecture-review.md) bij kwartaalreview

## Wanneer ADR verplicht

- Wijziging retrieval pipeline, auth model, of data schema
- Nieuwe externe afhankelijkheid met failover-impact
- Breaking API contract

Kleine refactors: geen ADR — wel [technical-debt-register.md](../ops/technical-debt-register.md) indien nodig.

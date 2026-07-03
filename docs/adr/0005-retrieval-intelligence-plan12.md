# ADR-0005: Plan12 retrieval intelligence focus

**Status:** Accepted  
**Date:** 2026-07-03  
**Context:** Plan11 closed with 1.0 eval baseline. Marginal gains require ranking, explainability, and routing depth.

## Decision

1. **Plan12** prioritizes retrieval intelligence over new corpus expansion.
2. **EXP-002** is the primary innovation bet (reranker A/B with latency guard).
3. **Explainability** fields become part of the standard query response contract.
4. **Long-tail eval** extends fixtures before raising recall thresholds again.

## Consequences

- Sustainability/competition domain promotion deferred to plan13+.
- Reranker changes require release eval + integration gate green.
- Router changes need `query_router_service` unit tests updated.

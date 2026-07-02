# ADR-0001: Portfolio planning and quarterly review cadence

**Status:** Accepted  
**Date:** 2026-07-02  
**Context:** Plan5 J1 vereist objective metrics, capacity model, en architecture review ritme.

## Decision

1. **Metrics** leven in `docs/product/portfolio-metrics.yaml` (single source of truth).
2. **Roadmap** per kwartaal in `docs/product/quarterly-roadmap.md` met expliciete debt-slots.
3. **Capacity** volgt healthy vs budget-burn modi in `docs/ops/capacity-model.md`.
4. **Debt** wordt bijgehouden in `docs/ops/technical-debt-register.md`.
5. **Review** einde elk kwartaal per `docs/ops/architecture-review.md`; gate via `run-quarterly-portfolio-review.sh`.

## Consequences

- Feature work pauzeert bij error-budget burn (geen ad-hoc uitzonderingen zonder log).
- Minimaal 15% capaciteit naar debt in healthy modus.
- Nieuwe structurele beslissingen krijgen ADR in `docs/adr/`.

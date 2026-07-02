# ADR-0002: Solo-first operating model with multi-team readiness

**Status:** Accepted  
**Date:** 2026-07-02  
**Context:** Plan8 vereist cross-team SLAs en operating model; team is solo met geplande groei.

## Decision

1. **Ownership matrix** in `docs/org/component-ownership-matrix.yaml` met logische teams (backend, frontend, ingestion, platform).
2. **Interface SLAs** in `docs/org/interface-slas.yaml` — meetbaar bij groei, nu documentair.
3. **Quality gates** geharmoniseerd in `docs/engineering/quality-gates.yaml` + audit script.
4. **Enablement** via playbooks en onboarding KPI's; review guild start als solo self-review.
5. **Capaciteit** blijft gesynchroniseerd via `sync-quarterly-capacity.sh` + bestaand portfolio ritme.

## Consequences

- Solo engineer draagt alle `on_call_primary` rollen tot hire #2.
- Release eval blijft lokaal/stack-afhankelijk; CI unit-only tot integration runner.
- Bij teamgroei: splits on-call per matrix zonder herstructurering.

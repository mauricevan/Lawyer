# ADR-0007: Plan14 enterprise reliability focus

**Status:** Accepted  
**Date:** 2026-07-03  
**Context:** Plan13 closed with lifecycle automation. Operational risk shifts to dependency failure, recovery time, and incident repeatability.

## Decision

1. **Plan14** prioritizes enterprise reliability over new product features.
2. **Failover** validation extends existing live-fallback and continuity plan with automated tests.
3. **Recovery drills** become a gated ops script, not ad-hoc manual runs.
4. **Incident response** links every Tier-1 alert to an executable runbook.

## Consequences

- New reliability scripts live under `scripts/ops/` and `scripts/platform/`.
- Breaking changes to health/readiness endpoints require ADR update.
- Feature work deferred unless tied to reliability SLOs.

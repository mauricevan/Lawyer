# ADR-0011: Immutable Legal Explanation Engine

**Status:** Accepted  
**Date:** 2026-07-05  
**Deciders:** Product / backend  
**Supersedes (partial):** post-compose V6–V10 revision path in agent pipeline  
**Related:** [legal_explanation_engine plan v3.1](/home/mau/.cursor/plans/legal_explanation_engine_6968183c.plan.md)

---

## Context

User-facing answers were mutated after LLM compose by pseudo-judicial services (court simulation, multi-judge panels, doctrine scoring). Sanitizers ran too late. Layperson UI exposed internal pipeline steps.

## Decision

Introduce a single-writer explanation engine with frozen drafts and atomic publish:

```
Retrieve → Compose → Verify → Publish → Render → Respond → (async telemetry)
```

| Component | Responsibility |
|---|---|
| `ExplanationComposerService` | **Only** writer of `LegalExplanationDraft` |
| `ExplanationPublishGuardService` | PASS → `PublishedExplanation`; FAIL → `GapResponse` (no repair) |
| `ExplanationRendererService` | Template-only markdown |
| `InternalAnalysisOrchestrator` | Optional async telemetry (`internal_simulation_telemetry_enabled=false` default) |

V6–V10 `*RevisionService.revise()` and simulation gates are **removed from the user pipeline**; libraries remain for isolated tests / future telemetry only.

## Invariants

1. **INV-E1** — No post-compose mutation of user-facing text in `AgentV4PipelineService`.
2. **INV-E2** — `LegalExplanationDraft`, `PublishedExplanation`, `GapResponse` are `frozen=True`.
3. **INV-E3** — Authority leak → deterministic `GapResponse` (`validation_failure`), never strip-in-place.
4. **INV-E4** — CI script `scripts/ci/check_explanation_immutability.sh` must stay green.
5. **INV-E5** — Layperson SSE steps limited to: clarifying, fetching, validating, generating, complete.

## Consequences

- **Positive:** Predictable, auditable explanations; no simulated court headings in production answers.
- **Negative:** Some internal analysis modules no longer affect user output until telemetry is explicitly enabled.
- **Testing:** Unit tests (`test_explanation_*`), golden leak detector, G3 Step 6 smoke, live C3 smoke (`EXPLANATION_LIVE_SMOKE=1`).

## Enforcement

- Grep CI: no `.revise()`, `*RevisionService`, simulation gates in pipeline.
- `has_authority_leak()` blocklist in publish guard.
- Backend restart required after deploy (stale uvicorn served pre-strip code during initial smoke).

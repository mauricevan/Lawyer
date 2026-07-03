# Plan13 kickoff — formal start decision (plan12 exit)

**Decision:** APPROVED — start `plan13.md`  
**Date:** 2026-07-03  
**Approver:** engineering (solo)

## Rationale

1. Plan12 exit criteria met — retrieval intelligence AA–AD closed with measurable long-tail gains
2. Corpus and eval quality stable; next risk is stale documents and manual reindex drift
3. Document model already has `indexed_at` / `modified_at` — ready for lifecycle automation

## Scope plan13 (confirmed)

- Automatic staleness detection (document vs index freshness)
- Reindex policy on legal version changes
- Deprecation and archive workflow
- Version conflict resolution and lifecycle metrics

## Capacity commit (Q1 2027 prep / Q4 2026 carry)

| Bucket | Hours/week |
|---|---|
| Features | 16 |
| Reliability | 8 |
| Debt | 8 |
| Ops/governance | 6 |
| Lifecycle automation | 6 |

## Entry gates met

- [x] `run-plan-transition-check.sh plan12`
- [x] Plan12 exit review documented
- [x] Long-tail eval `passed: true`
- [x] Integration eval in CI (TD-004)

## First actions plan13

1. Define staleness rules and scan script against `documents.indexed_at`
2. Wire reindex triggers to existing `run-reindex.sh` / ingest force path
3. Document deprecatie-archiefstroom in lifecycle register

## Sign-off

Solo self-review per [pair-review-policy.md](../engineering/pair-review-policy.md).

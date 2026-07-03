# Plan12 kickoff — formal start decision (plan11 exit)

**Decision:** APPROVED — start `plan12.md`  
**Date:** 2026-07-03  
**Approver:** engineering (solo)

## Rationale

1. Plan11 exit criteria met — all workstreams AA–AD closed, TD-004 resolved
2. Retrieval baseline at 1.0/1.0; next gains require ranking and explainability depth
3. EXP-002 (reranker A/B) is top-scored experiment in backlog

## Scope plan12 (confirmed)

- Advanced reranking experiments (EXP-002)
- Explainable retrieval output in API/UI
- Query-router intent library refinement
- Long-tail legal question eval harness

## Capacity commit (Q4 2026)

| Bucket | Hours/week |
|---|---|
| Features | 18 |
| Reliability | 8 |
| Debt | 6 |
| Ops/governance | 6 |
| Innovation (EXP-002) | 4 |

## Entry gates met

- [x] `run-plan-transition-check.sh plan11`
- [x] Plan11 exit review documented
- [x] Eval report `passed: true`
- [x] Integration eval in CI (TD-004)

## First actions plan12

1. Activate EXP-002 — reranker model swap with MRR/latency gate
2. Standardize retrieval explainability fields in query response
3. Extend eval fixture with long-tail / edge-case questions

## Sign-off

Solo self-review per [pair-review-policy.md](../engineering/pair-review-policy.md).

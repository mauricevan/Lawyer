# Plan12 exit review — cycle close (plan10 W)

**Decision:** APPROVED — close `plan12.md`, start `plan13.md`  
**Date:** 2026-07-03  
**Reviewer:** engineering (solo)

## Summary

Plan12 delivered retrieval intelligence: reranker A/B (EXP-002), explainable retrieval output, intent-based query routing, and long-tail eval harness. All workstreams AA–AD completed within Q4 2026 kickoff window.

## KPI results

| KPI | Target | Measured | Status |
|---|---|---|---|
| EXP-002 reranker gate | pass | control retained (MRR 1.0, p95 1343ms) | ✅ |
| p95 retrieval latency | < 10s | ~1.3s | ✅ |
| Long-tail recall@5 | ≥ 0.75 | 0.95 (20 vragen) | ✅ |
| Long-tail MRR | ≥ 0.65 | 0.84 | ✅ |
| Router intent eval | pass | 7/7 cases | ✅ |
| Release eval baseline | pass | retrieval 1.0 + longtail 0.95 | ✅ |

## Workstream completion

| Stream | Deliverable |
|---|---|
| AA | `reranker_models.yaml`, `run-reranker-ab-eval.sh`, EXP-002 done |
| AB | `retrieval_explainability`, pipeline refactor, UI panel |
| AC | `query_intent_library.yaml`, `DomainClusterService`, router eval |
| AD | `rag_eval_longtail.json`, `run-longtail-eval.sh`, baseline update |

## Deferred / carry-forward

| Item | Target plan | Notes |
|---|---|---|
| Reranker candidate promotion | backlog | No MRR lift at 1.0 ceiling; control default |
| Sustainability domain `go` | plan13+ | Still `pilot` in domain registry |
| LEG-002 eval script docs | mitigated | Suites documented in `eval-thresholds.yaml` |
| TD-001 NL-primary corpus | plan13+ | Lifecycle automation reduces manual reindex pain |

## Entry gates for plan13

- [x] Eval baseline current (incl. longtail suite)
- [x] `run-knowledge-base-check.sh` green
- [x] `run-quality-gate-audit.sh` green
- [x] `plan13-kickoff.md` APPROVED
- [x] Portfolio themes reprioritized in `next-cycle-themes.yaml`

## Sign-off

Solo self-review per [pair-review-policy.md](../engineering/pair-review-policy.md).

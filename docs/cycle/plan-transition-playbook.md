# Plan transition playbook — planN → planN+1 (plan10 W)

## When to transition

- All workstreams in planN checked off **or** explicit deferral in ADR
- Exit criteria met or mitigated with dated follow-up
- Next plan kickoff doc approved

## Standard steps

1. **Close** — update `planN.md` status, KPIs honest (✅/⏳)
2. **Handoff** — add overdracht line in planN → planN+1
3. **Verify** — `./scripts/ops/run-plan-transition-check.sh planN`
4. **Kickoff** — copy themes into next plan from [next-cycle-themes.yaml](./next-cycle-themes.yaml)
5. **Commit** — `docs: planN complete, start planN+1`

## Required artifacts per transition

| Artifact | Path |
|---|---|
| Eval baseline current | `backend/tests/fixtures/eval_baseline.json` |
| Knowledge base | `run-knowledge-base-check.sh` |
| Quality gates | `run-quality-gate-audit.sh` |
| Portfolio board | `run-portfolio-board-review.sh` (if strategic plan) |

## Plan relevance review

Every 2 plans or quarterly — run review from [plan-relevance-review.yaml](./plan-relevance-review.yaml).

## Legacy cleanup

Archive or complete items in [legacy-cleanup-register.yaml](./legacy-cleanup-register.yaml) before starting planN+2.

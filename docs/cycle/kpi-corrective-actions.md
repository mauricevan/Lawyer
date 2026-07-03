# KPI corrective actions (plan10 X)

## retrieval

**Trigger:** Recall@5 < 0.80 in release eval  
**Actions:**

1. Run domain + multilingual eval isolatie
2. Check Qdrant index freshness — `./scripts/platform/run-document-staleness-scan.sh`
3. Reindex drift — `./scripts/platform/run-lifecycle-reindex.sh` (zie [reindex-runbook.md](../ops/reindex-runbook.md))
4. Freeze prompt changes until green
5. Log in `incident-learnings.md` if production-impacting

## multilingual

**Trigger:** Multilingual suite < 0.70  
**Actions:**

1. Verify language fallback chain
2. Prioritize EXP-001 (native corpus) in experiment backlog
3. Update baseline only after intentional corpus change

## release-gate

**Trigger:** `run-release-eval-suite.sh` failed  
**Actions:**

1. Block deploy (`release-standards.md`)
2. Compare `eval-reports/latest.json` regressions
3. Rollback prompt config if P-change caused fail

## debt

**Trigger:** >0 open P1 debt items at quarter start  
**Actions:**

1. Switch to budget-burn capacity mode
2. Schedule top P1 in first 2 weeks of quarter
3. Update `technical-debt-register.md` Done-log

## risk

**Trigger:** >2 risks with exposure ≥ 12  
**Actions:**

1. Run `run-strategic-risk-review.sh`
2. Architecture review within 5 days
3. ADR for accepted residual risk

## innovation

**Trigger:** Active experiments > max in innovation-budget  
**Actions:**

1. Stop or complete lowest-scoring experiment
2. No new EXP-* until within budget

## retrospective link

Document outcomes in [org-retrospective-template.md](./org-retrospective-template.md).

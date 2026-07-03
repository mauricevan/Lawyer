# Plan15 kickoff — formal start decision (plan14 exit)

**Decision:** APPROVED — start `plan15.md`  
**Date:** 2026-07-03  
**Approver:** engineering (solo)

## Rationale

1. Plan14 exit criteria met — reliability workstreams AA–AD closed with release/quarterly gates
2. Dependency failure modes are tested and runbook-linked; next gap is product governance traceability
3. Policy decisions (risk acceptance, deprecation, rollout) need centralized audit trails for enterprise buyers

## Scope plan15 (confirmed)

- Policy-as-code foundations for product and legal guardrails
- Structured risk acceptance workflow with decision log
- Automated governance reporting for management and audit

## Capacity commit (Q1 2027 prep)

| Bucket | Hours/week |
|---|---|
| Features | 16 |
| Governance | 10 |
| Debt | 6 |
| Ops/governance | 6 |
| Reliability maintenance | 4 |

## Entry gates met

- [x] `run-plan-transition-check.sh plan14`
- [x] Plan14 exit review documented
- [x] Readiness pass-rate gate `passed: true`
- [x] Failover + recovery + incident audit gates green

## First actions plan15

1. Introduce central policy registry YAML with validation gate
2. Standardize risk acceptance workflow and decision log schema
3. Wire governance summary into admin dashboard

## Sign-off

Solo self-review per [pair-review-policy.md](../engineering/pair-review-policy.md).

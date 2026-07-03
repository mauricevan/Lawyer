# Runbook index (plan5 J2)

Centrale index — houd links actueel bij nieuwe runbooks.

## Operations

| Runbook | Wanneer |
|---|---|
| [release-checklist.md](../ops/release-checklist.md) | Vóór elke productie-deploy |
| [hotfix-runbook.md](../ops/hotfix-runbook.md) | P0/P1 productie-incident |
| [reindex-runbook.md](../ops/reindex-runbook.md) | Stale index / modified drift |
| [dependency-degradation-runbook.md](../ops/dependency-degradation-runbook.md) | `/ready` degraded / Tier-1 outage |
| [post-release-review.md](../ops/post-release-review.md) | Binnen 48u na release |
| [error-budget-policy.md](../ops/error-budget-policy.md) | SLO-overschrijding |
| [escalation-matrix.md](../ops/escalation-matrix.md) | Wie bellen |
| [architecture-review.md](../ops/architecture-review.md) | Einde kwartaal |
| [alert-fatigue-review.md](../ops/alert-fatigue-review.md) | Wekelijks on-call |

## Observability

| Runbook | Wanneer |
|---|---|
| [top-5-incidents.md](../../observability/runbooks/top-5-incidents.md) | Alert of degradatie |
| [troubleshooting.md](./troubleshooting.md) | Onbekend symptoom |

## Security

| Runbook | Wanneer |
|---|---|
| [secret-rotation-playbook.md](../security/secret-rotation-playbook.md) | Geplande rotatie |
| [incident-key-exposure.md](../security/incident-key-exposure.md) | Mogelijk gelekt secret |
| [pentest-findings.md](../security/pentest-findings.md) | Security review |

## Product / QA

| Runbook | Wanneer |
|---|---|
| [feedback-triage.md](../product/feedback-triage.md) | Wekelijkse feedback |
| [plan5-kpi-scorecard.md](../product/plan5-kpi-scorecard.md) | Maandelijks / kwartaal KPI |
| [run-plan5-kpi-snapshot.sh](../../scripts/ops/run-plan5-kpi-snapshot.sh) | KPI meting |
| [run-retrieval-eval.sh](../../scripts/qa/run-retrieval-eval.sh) | Release kwaliteitsgate |
| [run-domain-benchmark.sh](../../scripts/qa/run-domain-benchmark.sh) | Domein go/no-go |
| [run-multilingual-eval.sh](../../scripts/qa/run-multilingual-eval.sh) | Taaluitrol |
| [run-ingest-multilingual-seed.sh](../../scripts/qa/run-ingest-multilingual-seed.sh) | Native FR/DE/ES corpus |
| [run-legal-compliance-check.sh](../../scripts/qa/run-legal-compliance-check.sh) | Compliance docs + escalation |
| [run-document-staleness-scan.sh](../../scripts/platform/run-document-staleness-scan.sh) | Lifecycle staleness gate |
| [run-lifecycle-reindex.sh](../../scripts/platform/run-lifecycle-reindex.sh) | Drift reindex automation |
| [run-deprecation-register-check.sh](../../scripts/platform/run-deprecation-register-check.sh) | Deprecation register gate |
| [run-lifecycle-eval-gate.sh](../../scripts/platform/run-lifecycle-eval-gate.sh) | Release lifecycle gate (plan13 AD) |
| [run-readiness-check.sh](../../scripts/platform/run-readiness-check.sh) | Dependency readiness probe |
| [run-readiness-pass-rate-gate.sh](../../scripts/platform/run-readiness-pass-rate-gate.sh) | Readiness pass-rate SLO gate |
| [run-failover-eval.sh](../../scripts/qa/run-failover-eval.sh) | Simulated Qdrant failover eval |
| [run-recovery-drill-gate.sh](../../scripts/ops/run-recovery-drill-gate.sh) | Quarterly recovery MTTR gate |
| [run-incident-playbook-audit.sh](../../scripts/ops/run-incident-playbook-audit.sh) | Tier-1 alert runbook coverage |
| [run-version-conflict-scan.sh](../../scripts/platform/run-version-conflict-scan.sh) | Version conflict scan |
| [document-lifecycle.md](../../docs/data/document-lifecycle.md) | Lifecycle states & archive |
| [run-integration-eval-gate.sh](../../scripts/qa/run-integration-eval-gate.sh) | CI integration eval (TD-004) |
| [run-stack-aware-eval.sh](../../scripts/qa/run-stack-aware-eval.sh) | Release eval met stack-check |

## Scripts

```bash
./scripts/ops/run-release-checklist.sh
./scripts/ops/run-hotfix-rollback.sh
./scripts/ops/run-quarterly-portfolio-review.sh
./scripts/ops/run-portfolio-board-review.sh
./scripts/ops/run-innovation-pipeline-check.sh
./scripts/ops/run-strategic-risk-review.sh
./scripts/ops/run-cycle-planning-review.sh
./scripts/ops/run-kpi-catalog-review.sh
./scripts/ops/run-plan-transition-check.sh plan9
./scripts/ops/run-knowledge-base-check.sh
./scripts/ops/check-pair-review.sh
./scripts/ops/run-plan5-kpi-snapshot.sh
./scripts/platform/run-self-service.sh
./scripts/ops/run-release-pipeline.sh
./scripts/dev/bootstrap.sh
```

## Onderhoud

- **Maandelijks:** verifieer dat alle links in dit document werken
- **Per incident:** update [incident-learnings.md](./incident-learnings.md) + relevant runbook
- **Per kwartaal:** review tijdens [architecture-review.md](../ops/architecture-review.md)

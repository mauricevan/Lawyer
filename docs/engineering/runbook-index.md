# Runbook index (plan5 J2)

Centrale index — houd links actueel bij nieuwe runbooks.

## Operations

| Runbook | Wanneer |
|---|---|
| [release-checklist.md](../ops/release-checklist.md) | Vóór elke productie-deploy |
| [hotfix-runbook.md](../ops/hotfix-runbook.md) | P0/P1 productie-incident |
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
| [run-retrieval-eval.sh](../../scripts/qa/run-retrieval-eval.sh) | Release kwaliteitsgate |
| [run-domain-benchmark.sh](../../scripts/qa/run-domain-benchmark.sh) | Domein go/no-go |
| [run-multilingual-eval.sh](../../scripts/qa/run-multilingual-eval.sh) | Taaluitrol |

## Scripts

```bash
./scripts/ops/run-release-checklist.sh
./scripts/ops/run-hotfix-rollback.sh
./scripts/ops/run-quarterly-portfolio-review.sh
./scripts/ops/run-knowledge-base-check.sh
./scripts/ops/check-pair-review.sh
```

## Onderhoud

- **Maandelijks:** verifieer dat alle links in dit document werken
- **Per incident:** update [incident-learnings.md](./incident-learnings.md) + relevant runbook
- **Per kwartaal:** review tijdens [architecture-review.md](../ops/architecture-review.md)

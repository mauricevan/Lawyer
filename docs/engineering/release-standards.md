# Release standards (plan8 R)

Uniforme release-flow voor alle teams. Geen ad-hoc deploys.

## Pre-merge (elke PR)

| Gate | Commando | Blokkeert |
|---|---|---|
| Unit tests | `pytest backend/tests -m "not integration" -q` | merge |
| Frontend tests | `cd frontend && npm test -- --run` | merge (bij UI) |
| Secret scan | pre-commit / CI `check-secrets.sh` | merge |
| Pair review | `check-pair-review.sh` | merge (kritieke paden) |
| Knowledge base | `run-knowledge-base-check.sh` | merge (doc PRs) |

## Pre-release (tag / deploy)

```bash
./scripts/ops/run-release-pipeline.sh --with-eval
```

Stappen:

1. Release checklist (`run-release-checklist.sh`)
2. Stack verify (`verify-stack.sh` indien backend draait)
3. Eval suite met baseline (`run-release-eval-suite.sh`)

## Rollback

| Type | Actie |
|---|---|
| App | `docs/ops/hotfix-runbook.md` |
| Prompts | `scripts/qa/rollback-prompt-config.sh` |
| Data | dataset changelog + reindex runbook |

## Versiebeheer

- API: `/api/v1/...` — breaking changes → nieuwe versie
- Prompts/datasets: bump `version` in YAML + changelog entry
- Eval baseline: `--update-baseline` alleen na bewuste verbetering

## Quality gate audit

```bash
./scripts/ops/run-quality-gate-audit.sh
```

Valideert dat gates gedocumenteerd en scripts aanwezig zijn.

Zie: [quality-gates.yaml](./quality-gates.yaml), [definition-of-done.md](./definition-of-done.md)

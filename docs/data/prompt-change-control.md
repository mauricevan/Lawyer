# Prompt change control (plan7 P)

## Scope

- `shared/config/prompts.yaml` — system prompts, mode hints, follow-up hint
- `shared/config/retrieval_params.yaml` — documented retrieval defaults (runtime via env)

## Process

1. Open PR with YAML diff only (no inline prompt edits in `llm_service.py`).
2. Run pair review: `PAIR_REVIEW_ACK=yes ./scripts/ops/check-pair-review.sh`
3. Run eval suite: `./scripts/qa/run-release-eval-suite.sh`
4. Document change in PR description with expected quality impact.

## Rollback

```bash
./scripts/qa/rollback-prompt-config.sh
```

Restores last committed `prompts.yaml` and `retrieval_params.yaml`.

## Version field

Bump `version` in both YAML files on every production-impacting change.

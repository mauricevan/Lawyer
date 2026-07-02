# Experiment policy (plan7 P)

## Allowed without full release

- Threshold tuning within `docs/data/eval-thresholds.yaml` if metrics improve
- Non-production env prompt A/B via env-specific config copy

## Requires eval gate + pair review

- System prompt or mode hint changes
- Retrieval parameter changes affecting `RagService` behavior
- New eval fixtures or baseline updates

## A/B evaluation

1. Branch with config change
2. `./scripts/qa/run-release-eval-suite.sh` vs baseline
3. Compare `docs/data/eval-reports/latest.json`
4. Merge only if `passed: true` or documented exception in ADR

## Prohibited

- Direct production edits without version bump
- Prompt changes during incident without post-mortem note
- Skipping baseline comparison on release pipeline `--with-eval`

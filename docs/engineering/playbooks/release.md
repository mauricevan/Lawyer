# Playbook: release (plan8 S)

## Wanneer

Elke deploy naar staging/productie of significante tag op `main`.

## Checklist

```bash
./scripts/ops/run-release-pipeline.sh --with-eval
./scripts/ops/run-quality-gate-audit.sh
./scripts/ops/run-enablement-check.sh   # optioneel, doc drift
```

## Beslisboom

| Eval `passed` | Actie |
|---|---|
| true | Deploy + noteer versie in changelog |
| false | Geen deploy; fix of baseline update met motivatie |
| stack down | Deploy zonder eval alleen hotfix P0; eval direct na |

## Post-release

1. `verify-stack.sh` op doelomgeving
2. Smoke query via frontend of `curl` API
3. Update `docs/data/eval-reports/latest.json` in repo indien baseline-run

## Rollback

Zie [release-standards.md](../release-standards.md) rollback-tabel.

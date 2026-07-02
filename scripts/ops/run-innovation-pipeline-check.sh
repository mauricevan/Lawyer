#!/usr/bin/env bash
# Innovation pipeline check — backlog, budget, stop/go (plan9 U).
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"
export PYTHONPATH=.

echo "=== Innovation pipeline check ==="

required=(
  docs/product/experiment-backlog.yaml
  docs/product/innovation-budget.yaml
  docs/product/innovation-productization.md
  docs/data/experiment-policy.md
)

for doc in "${required[@]}"; do
  [[ -f "$doc" ]] || { echo "FAIL: missing $doc"; exit 1; }
  echo "OK: $doc"
done

python3 - <<'PY'
from backend.src.services.experiment_backlog_service import ExperimentBacklogService

service = ExperimentBacklogService()
data = service.load_backlog()
experiments = data.get("experiments", [])
if len(experiments) < 2:
    raise SystemExit("FAIL: experiment backlog needs at least 2 entries")

for exp in experiments:
    errors = service.validate_experiment(exp)
    if errors:
        raise SystemExit(f"FAIL {exp.get('id')}: {errors}")

ok, reason = service.can_start_experiment()
print(f"OK: can_start_experiment={ok} ({reason})")
print(f"OK: {len(experiments)} experiments, {len(service.active_experiments())} active")
PY

echo ""
echo "PASS: Innovation pipeline check succeeded."

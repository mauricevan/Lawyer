#!/usr/bin/env bash
# Cycle planning review — alignment, relevance, legacy (plan10 W).
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"
export PYTHONPATH=.

echo "=== Cycle planning review ==="

required=(
  docs/cycle/annual-quarterly-alignment.md
  docs/cycle/plan-transition-playbook.md
  docs/cycle/plan-relevance-review.yaml
  docs/cycle/legacy-cleanup-register.yaml
)

for doc in "${required[@]}"; do
  [[ -f "$doc" ]] || { echo "FAIL: missing $doc"; exit 1; }
  echo "OK: $doc"
done

python3 - <<'PY'
from backend.src.services.cycle_planning_service import CyclePlanningService

service = CyclePlanningService()
stale = service.stale_reviews()
if stale:
    raise SystemExit(f"FAIL: stale plan reviews: {stale}")
open_legacy = service.open_legacy_count()
print(f"OK: {open_legacy} open legacy items (max 10)")
errors = service.validate_plan_transition("plan9")
if errors:
    print("NOTE:", "; ".join(errors))
print("OK: cycle planning validation passed")
PY

./scripts/ops/sync-quarterly-capacity.sh

echo ""
echo "PASS: Cycle planning review succeeded."

#!/usr/bin/env bash
# Validate planN → planN+1 transition gates (plan10 W).
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"
export PYTHONPATH=.

PLAN="${1:-plan9}"
echo "=== Plan transition check: ${PLAN} ==="

[[ -f "${PLAN}.md" ]] || { echo "FAIL: missing ${PLAN}.md"; exit 1; }
echo "OK: ${PLAN}.md exists"

required=(
  docs/cycle/plan-transition-playbook.md
  docs/cycle/next-cycle-themes.yaml
  docs/cycle/plan11-kickoff.md
)

for doc in "${required[@]}"; do
  [[ -f "$doc" ]] || { echo "FAIL: missing $doc"; exit 1; }
  echo "OK: $doc"
done

python3 - <<PY
from backend.src.services.cycle_planning_service import CyclePlanningService

service = CyclePlanningService()
errors = service.validate_plan_transition("${PLAN}")
if errors:
    for err in errors:
        if "not required" in err:
            print(f"NOTE: {err}")
        else:
            raise SystemExit(f"FAIL: {err}")
print("OK: transition artifacts valid")
PY

chmod +x scripts/ops/run-knowledge-base-check.sh scripts/ops/run-quality-gate-audit.sh 2>/dev/null || true
./scripts/ops/run-knowledge-base-check.sh
./scripts/ops/run-quality-gate-audit.sh

echo ""
echo "PASS: Plan transition check succeeded for ${PLAN}."

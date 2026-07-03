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

readarray -t DYNAMIC_DOCS < <(python3 - <<'PY'
import yaml
from pathlib import Path

data = yaml.safe_load(Path("docs/cycle/next-cycle-themes.yaml").read_text(encoding="utf-8"))
start = data.get("formal_start", {})
for key in ("kickoff_doc", "exit_review_doc"):
    path = start.get(key)
    if path:
        print(path)
PY
)

required=(
  docs/cycle/plan-transition-playbook.md
  docs/cycle/next-cycle-themes.yaml
)

for doc in "${required[@]}" "${DYNAMIC_DOCS[@]}"; do
  [[ -f "$doc" ]] || { echo "FAIL: missing $doc"; exit 1; }
  echo "OK: $doc"
done

python3 - <<PY
from backend.src.services.cycle_planning_service import CyclePlanningService

service = CyclePlanningService()
errors = service.validate_plan_transition("${PLAN}")
if errors:
    for err in errors:
        raise SystemExit(f"FAIL: {err}")
print("OK: transition artifacts valid")
PY

chmod +x scripts/ops/run-knowledge-base-check.sh scripts/ops/run-quality-gate-audit.sh 2>/dev/null || true
./scripts/ops/run-knowledge-base-check.sh
./scripts/ops/run-quality-gate-audit.sh

echo ""
echo "PASS: Plan transition check succeeded for ${PLAN}."

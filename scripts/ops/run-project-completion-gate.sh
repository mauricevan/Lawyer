#!/usr/bin/env bash
# Project completion gate — pytest + all release gates (plan31 AC).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"
export PYTHONPATH=.

echo "=== Project completion gate ==="
pytest backend/tests -m "not integration" -q

gates=(
  scripts/platform/run-policy-registry-gate.sh
  scripts/platform/run-partner-api-gate.sh
  scripts/qa/run-failover-eval.sh
  scripts/platform/run-readiness-pass-rate-gate.sh
  scripts/ops/run-incident-playbook-audit.sh
  scripts/ops/run-governance-snapshot.sh
  scripts/platform/run-cycle-plan-gate.sh
)

for gate in "${gates[@]}"; do
  echo "→ $gate"
  if [[ "$gate" == *cycle-plan-gate* ]]; then
    CI=true bash "$gate" --all
  elif [[ "$gate" == *readiness-pass-rate* ]]; then
    CI=true bash "$gate"
  else
    bash "$gate"
  fi
done

python3 backend/scripts/run_project_completion_gate.py
echo "PASS: Project completion gate succeeded"

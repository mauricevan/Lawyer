#!/usr/bin/env bash
# Cycle plan deliverable gate (plan16–plan30).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT" && export PYTHONPATH=.
if [[ "${1:-}" == "--all" ]]; then
  python3 backend/scripts/run_cycle_plan_gate.py --all
else
  python3 backend/scripts/run_cycle_plan_gate.py --plan "${1:?usage: run-cycle-plan-gate.sh plan16 | --all}"
fi
echo "PASS: Cycle plan gate succeeded"

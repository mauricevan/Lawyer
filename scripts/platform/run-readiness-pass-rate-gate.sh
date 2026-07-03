#!/usr/bin/env bash
# Readiness pass-rate SLO gate — target ≥ 99% (plan14 KPI).
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"
export PYTHONPATH=.

MODE_ARGS=()
if [[ "${SIMULATE:-false}" == "true" ]]; then
  MODE_ARGS+=(--simulate)
fi

python3 backend/scripts/run_readiness_pass_rate_gate.py "${MODE_ARGS[@]}" "$@"
echo "→ Report: docs/data/reliability-reports/readiness-pass-rate-latest.json"
echo "PASS: Readiness pass-rate gate succeeded"

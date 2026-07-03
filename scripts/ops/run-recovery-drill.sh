#!/usr/bin/env bash
# Recovery drill with MTTR report (plan14 AC).
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"
export PYTHONPATH=.

MODE_ARGS=()
if [[ "${SIMULATE:-false}" == "true" ]]; then
  MODE_ARGS+=(--simulate)
fi

echo "=== Recovery drill (automated) ==="
echo "Runbook: docs/ops/recovery-drill.md"
python3 backend/scripts/run_recovery_drill.py "${MODE_ARGS[@]}" "$@"
echo "→ Report: docs/data/reliability-reports/recovery-drill-latest.json"
echo "PASS: Recovery drill complete"

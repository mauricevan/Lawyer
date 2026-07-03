#!/usr/bin/env bash
# Quarterly recovery drill gate — MTTR + report freshness (plan14 AC).
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"
export PYTHONPATH=.

python3 backend/scripts/run_recovery_drill.py --gate "$@"
echo "PASS: Recovery drill gate succeeded"

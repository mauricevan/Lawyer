#!/usr/bin/env bash
# Offline failover scenario eval — simulated Qdrant loss (plan14 AB).
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"
export PYTHONPATH=.

python3 backend/scripts/run_failover_eval.py "$@"
echo "→ Report: docs/data/reliability-reports/failover-latest.json"
echo "PASS: Failover eval succeeded"

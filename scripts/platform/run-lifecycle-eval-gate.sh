#!/usr/bin/env bash
# Lifecycle eval gate — deprecation, version policy, optional staleness (plan13 AD).
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"
export PYTHONPATH=.

python3 backend/scripts/run_lifecycle_eval_gate.py "$@"
echo "PASS: Lifecycle eval gate succeeded"

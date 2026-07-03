#!/usr/bin/env bash
# Policy-as-code registry validation gate (plan15 AA).
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"
export PYTHONPATH=.

python3 backend/scripts/run_policy_registry_gate.py "$@"
echo "→ Report: docs/data/governance-reports/policy-registry-latest.json"
echo "PASS: Policy registry gate succeeded"

#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT" && export PYTHONPATH=.
python3 backend/scripts/run_risk_acceptance_gate.py "$@"
echo "PASS: Risk acceptance gate succeeded"

#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT" && export PYTHONPATH=.
python3 backend/scripts/run_decision_log_audit.py "$@"
echo "PASS: Decision log audit succeeded"

#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT" && export PYTHONPATH=.
python3 backend/scripts/run_governance_snapshot.py "$@"
echo "PASS: Governance snapshot succeeded"

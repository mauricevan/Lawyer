#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT" && export PYTHONPATH=.
python3 backend/scripts/run_partner_api_gate.py "$@"
echo "PASS: Partner API gate succeeded"

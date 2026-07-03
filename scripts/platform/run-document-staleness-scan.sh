#!/usr/bin/env bash
# Document index staleness scan (plan13 AA).
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"
export PYTHONPATH=.

python3 backend/scripts/run_document_staleness_scan.py "$@"
echo "→ Report: docs/data/lifecycle-reports/staleness-latest.json"

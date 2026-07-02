#!/usr/bin/env bash
# Release eval suite with baseline comparison (plan7 O).
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"
export PYTHONPATH=.

UPDATE=false
for arg in "$@"; do
  case "$arg" in
    --update-baseline) UPDATE=true ;;
  esac
done

if [[ "$UPDATE" == true ]]; then
  python3 backend/scripts/run_eval_suite.py --update-baseline
  exit 0
fi

python3 backend/scripts/run_eval_suite.py
echo "Report: docs/data/eval-reports/latest.json"

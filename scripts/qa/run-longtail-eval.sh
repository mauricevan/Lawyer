#!/usr/bin/env bash
# Long-tail retrieval eval — requires Qdrant + seeded corpus (plan12 AD).
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"
export PYTHONPATH=.

python3 backend/scripts/build_longtail_eval_fixture.py >/dev/null
python3 backend/scripts/run_longtail_eval.py "$@"
echo "→ Report: docs/data/eval-reports/longtail-latest.json"

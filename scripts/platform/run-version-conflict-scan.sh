#!/usr/bin/env bash
# Version conflict scan — curated registration + optional indexed scan (plan13 AD).
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"
export PYTHONPATH=.

CURATED_ONLY="${CURATED_ONLY:-false}"
args=()
if [[ "$CURATED_ONLY" == "true" ]]; then
  args+=(--curated-only)
fi

python3 backend/scripts/run_version_conflict_scan.py "${args[@]}" "$@"
echo "→ Report: docs/data/lifecycle-reports/version-conflicts-latest.json"

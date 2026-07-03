#!/usr/bin/env bash
# Lifecycle reindex — drift and never-indexed curated docs (plan13 AB).
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"
export PYTHONPATH=.

DELAY="${DELAY_SECONDS:-2.0}"

echo "=== Lifecycle reindex (modified drift + never indexed) ==="
python3 backend/scripts/run_lifecycle_reindex.py --delay-seconds "$DELAY" "$@"
echo "→ Backfill chunk text for FTS"
python3 backend/scripts/backfill_chunk_text.py
echo "→ Report: docs/data/lifecycle-reports/reindex-latest.json"
echo "PASS: Lifecycle reindex complete"

#!/usr/bin/env bash
# Standardized curated corpus re-index (plan6 K2).
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"
export PYTHONPATH=.

LIMIT="${LIMIT:-0}"
FROM_CELEX="${FROM_CELEX:-}"
FORCE_CELEX="${FORCE_CELEX:-}"

args=()
if [[ "$LIMIT" -gt 0 ]]; then
  args+=(--limit "$LIMIT")
fi
if [[ -n "$FROM_CELEX" ]]; then
  args+=(--from-celex "$FROM_CELEX")
fi
if [[ -n "$FORCE_CELEX" ]]; then
  args+=(--force-celex "$FORCE_CELEX")
fi

echo "=== Re-index curated corpus ==="
python3 ingestion/scripts/ingest_curated.py "${args[@]}"
echo "→ Backfill chunk text for FTS"
python3 backend/scripts/backfill_chunk_text.py
echo "PASS: Re-index complete"

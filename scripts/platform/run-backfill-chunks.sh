#!/usr/bin/env bash
# Backfill chunks.text from Qdrant payloads (plan6 K2).
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"
export PYTHONPATH=.

echo "=== Backfill chunk text ==="
python3 backend/scripts/backfill_chunk_text.py
echo "PASS: Backfill complete"

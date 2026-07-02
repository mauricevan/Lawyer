#!/usr/bin/env bash
# Ingest native FR/DE/ES seed corpus for multilingual eval (plan11 AA).
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"
export PYTHONPATH=.

LANGUAGES="${LANGUAGES:-fr,de,es}"
FORCE=false
for arg in "$@"; do
  case "$arg" in
    --force-reindex) FORCE=true ;;
  esac
done

ARGS=(--languages "$LANGUAGES")
if [[ "$FORCE" == true ]]; then
  ARGS+=(--force-reindex)
fi

python3 ingestion/scripts/ingest_multilingual_seed.py "${ARGS[@]}"
echo "→ Run eval: ./scripts/qa/run-multilingual-eval.sh"

#!/usr/bin/env bash
# CI integration eval gate: seed offline corpus + subset eval (plan11 AD / TD-004).
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"
export PYTHONPATH=.
export USE_LOCAL_EMBEDDINGS="${USE_LOCAL_EMBEDDINGS:-true}"

QDRANT_URL="${QDRANT_URL:-http://localhost:6333}"
echo "=== Integration eval gate ==="

for _ in $(seq 1 30); do
  if curl -sf "${QDRANT_URL}/collections" >/dev/null 2>&1; then
    break
  fi
  sleep 2
done
curl -sf "${QDRANT_URL}/collections" >/dev/null || { echo "FAIL: Qdrant not ready"; exit 1; }

chmod +x scripts/qa/check-eval-stack.sh
if ! DATABASE_URL="${DATABASE_URL:-}" ./scripts/qa/check-eval-stack.sh >/dev/null 2>&1; then
  echo "WARN: Postgres check skipped or failed — continuing with Qdrant only"
fi

python3 ingestion/scripts/seed_ci_eval_corpus.py
python3 backend/scripts/run_eval_suite.py --ci
echo ""
echo "PASS: Integration eval gate succeeded."

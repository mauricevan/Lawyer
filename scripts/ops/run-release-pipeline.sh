#!/usr/bin/env bash
# Consolidated release pipeline: gates, verify, optional eval (plan6 K3).
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"

RUN_EVAL=false
for arg in "$@"; do
  case "$arg" in
    --with-eval) RUN_EVAL=true ;;
  esac
done

echo "=== Release pipeline ==="
chmod +x scripts/ops/run-release-checklist.sh scripts/observability/verify-stack.sh
./scripts/ops/run-release-checklist.sh

BACKEND_URL="${BACKEND_URL:-http://127.0.0.1:8001}"
if curl -sf "${BACKEND_URL}/health" >/dev/null 2>&1; then
  BACKEND_URL="$BACKEND_URL" ./scripts/observability/verify-stack.sh
else
  echo "NOTE: backend not running — skip observability verify"
fi

if [[ "$RUN_EVAL" == true ]]; then
  echo "→ Retrieval eval gate"
  PYTHONPATH=. ./scripts/qa/run-retrieval-eval.sh
fi

echo ""
echo "PASS: Release pipeline complete"
echo "Manual: docs/ops/release-checklist.md post-deploy section"

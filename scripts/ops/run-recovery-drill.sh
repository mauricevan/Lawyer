#!/usr/bin/env bash
# Recovery drill: rollback features + health verify (plan6 L2).
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"
BACKEND_URL="${BACKEND_URL:-http://127.0.0.1:8001}"

echo "=== Recovery drill ==="
echo "Runbook: docs/ops/recovery-drill.md"
echo ""

chmod +x scripts/ops/run-hotfix-rollback.sh scripts/ops/rollback-features.sh
./scripts/ops/run-hotfix-rollback.sh --verify-only || {
  echo "WARN: health check failed before drill — continuing mitigation test"
}

echo "→ Apply feature rollback (mitigation)"
./scripts/ops/rollback-features.sh

if docker compose ps -q backend 2>/dev/null | grep -q .; then
  echo "→ Restart backend"
  docker compose -f docker-compose.yml -f docker-compose.local.yml restart backend 2>/dev/null || true
  sleep 5
fi

./scripts/ops/run-hotfix-rollback.sh --verify-only
echo ""
echo "PASS: Recovery drill complete — document MTTR in post-mortem if real incident"

#!/usr/bin/env bash
# Hotfix rollback helper — target stable state within 5 minutes.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"

ENV_FILE="${ENV_FILE:-.env}"
BACKEND_URL="${BACKEND_URL:-http://127.0.0.1:8001}"
VERIFY_ONLY=false

for arg in "$@"; do
  case "$arg" in
    --verify-only) VERIFY_ONLY=true ;;
  esac
done

verify_health() {
  curl -sf "${BACKEND_URL}/health" >/dev/null
  curl -sf "${BACKEND_URL}/ready" >/dev/null
  echo "Health checks OK (${BACKEND_URL})"
}

if [[ "$VERIFY_ONLY" == true ]]; then
  verify_health
  exit 0
fi

echo "=== Hotfix rollback: disabling risky features ==="
chmod +x scripts/ops/rollback-features.sh
./scripts/ops/rollback-features.sh "$ENV_FILE"

echo "→ Restart services (if docker compose is running)"
if docker compose ps -q backend 2>/dev/null | grep -q .; then
  docker compose -f docker-compose.yml -f docker-compose.local.yml restart backend celery-worker 2>/dev/null || true
fi

sleep 3
verify_health

echo ""
echo "PASS: Hotfix mitigation applied. Complete image/tag rollback if still degraded."
echo "See docs/ops/hotfix-runbook.md"

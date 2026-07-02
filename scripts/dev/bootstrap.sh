#!/usr/bin/env bash
# Fast local developer bootstrap (plan6 M1).
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"
export PYTHONPATH=.

WITH_SEED=false
for arg in "$@"; do
  case "$arg" in
    --seed) WITH_SEED=true ;;
  esac
done

echo "=== Dev bootstrap ==="
if command -v docker >/dev/null 2>&1; then
  docker compose -f docker-compose.yml -f docker-compose.local.yml up -d postgres qdrant redis backend
  echo "→ Waiting for backend..."
  for _ in $(seq 1 30); do
    if curl -sf http://127.0.0.1:8001/health >/dev/null 2>&1; then
      break
    fi
    sleep 2
  done
else
  echo "Docker not found — use scripts/start_local.sh"
  exit 1
fi

echo "→ Migrations"
(cd backend && alembic upgrade head)

if [[ "$WITH_SEED" == true ]]; then
  ./scripts/dev/provision-test-data.sh
fi

chmod +x scripts/platform/check-env-parity.sh
./scripts/platform/check-env-parity.sh

echo ""
echo "PASS: Bootstrap complete"
echo "  API:      http://127.0.0.1:8001/docs"
echo "  Frontend: cd frontend && npm run dev"

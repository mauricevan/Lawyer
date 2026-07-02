#!/usr/bin/env bash
# Purge expired user data per retention policy (requires admin write access if configured).
set -euo pipefail

API_URL="${BACKEND_URL:-http://127.0.0.1:8001}"
ADMIN_KEY="${ADMIN_API_KEY:-}"

headers=()
if [[ -n "$ADMIN_KEY" ]]; then
  headers+=(-H "X-Admin-Key: ${ADMIN_KEY}")
fi

curl -fsS "${headers[@]}" "${API_URL}/api/v1/admin/retention/policy"
echo ""
curl -fsS "${headers[@]}" "${API_URL}/api/v1/admin/retention/status"
echo ""
curl -fsS -X POST "${headers[@]}" "${API_URL}/api/v1/admin/retention/purge"
echo ""

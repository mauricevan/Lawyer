#!/usr/bin/env bash
# Purge audit logs older than AUDIT_RETENTION_DAYS (requires admin API key if configured).
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
API_URL="${BACKEND_URL:-http://127.0.0.1:8001}"
ADMIN_KEY="${ADMIN_API_KEY:-}"

headers=()
if [[ -n "$ADMIN_KEY" ]]; then
  headers+=(-H "X-Admin-Key: ${ADMIN_KEY}")
fi

curl -fsS "${headers[@]}" "${API_URL}/api/v1/admin/audit/retention"
echo ""
curl -fsS -X POST "${headers[@]}" "${API_URL}/api/v1/admin/audit/retention/purge"
echo ""

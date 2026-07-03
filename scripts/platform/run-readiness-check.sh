#!/usr/bin/env bash
# Readiness probe check — Postgres, Qdrant, Redis (plan14 AA).
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"
export PYTHONPATH=.

BACKEND_URL="${BACKEND_URL:-http://localhost:8001}"

echo "=== Readiness check: ${BACKEND_URL}/ready ==="
response="$(curl -s -w "\n%{http_code}" "${BACKEND_URL}/ready")"
body="$(echo "$response" | head -n -1)"
code="$(echo "$response" | tail -n 1)"
echo "$body" | python3 -m json.tool
if [[ "$code" != "200" ]]; then
  echo "FAIL: /ready returned HTTP ${code}"
  exit 1
fi
echo "PASS: Readiness OK"

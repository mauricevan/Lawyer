#!/usr/bin/env bash
# Fail when backend logging may emit raw secrets.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"

FAILURES=0
TARGET="backend/src"

while IFS= read -r match; do
  [[ -z "$match" ]] && continue
  case "$match" in
    *auth_service.py*|*routes/auth.py*|*tables.py*)
      continue
      ;;
  esac
  echo "LOG RISK: $match"
  FAILURES=$((FAILURES + 1))
done < <(
  grep -rnE "logger\.(debug|info|warning|error|exception)\(.*(password|api_key|jwt_secret|admin_api_key|OPENROUTER)" "$TARGET" 2>/dev/null || true
)

if [[ "$FAILURES" -gt 0 ]]; then
  echo "Log output scan failed with $FAILURES issue(s)."
  exit 1
fi

echo "Log output scan passed."

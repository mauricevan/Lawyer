#!/usr/bin/env bash
# Disable risky features quickly during incidents.
set -euo pipefail

ENV_FILE="${1:-.env}"

update_flag() {
  local key="$1"
  local value="$2"
  if rg -q "^${key}=" "$ENV_FILE"; then
    sed -i "s/^${key}=.*/${key}=${value}/" "$ENV_FILE"
  else
    echo "${key}=${value}" >> "$ENV_FILE"
  fi
}

update_flag FEATURE_FLAG_LIVE_FALLBACK false
update_flag ENABLE_LIVE_FALLBACK false
update_flag FEATURE_FLAG_AUTO_UPGRADE false
update_flag ENABLE_CELERY_INGEST false

echo "Risky features disabled in ${ENV_FILE}. Restart backend and workers."

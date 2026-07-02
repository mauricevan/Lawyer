#!/usr/bin/env bash
# Enable staged rollout of Lawyer feature flags.
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

update_flag FEATURE_FLAG_LIVE_FALLBACK true
update_flag FEATURE_FLAG_HYBRID_RRF true
update_flag FEATURE_FLAG_AUTO_UPGRADE true
update_flag FEATURE_FLAG_AUDIT_LOGGING true
update_flag ENABLE_LIVE_FALLBACK true
update_flag ENABLE_REDIS_CACHE true
update_flag ENABLE_CELERY_INGEST true

echo "Feature flags enabled in ${ENV_FILE}. Restart backend and workers."

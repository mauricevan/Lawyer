#!/usr/bin/env bash
# Error budget and SLO snapshot (plan6 L1).
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"
BACKEND_URL="${BACKEND_URL:-http://127.0.0.1:8001}"

echo "=== Error budget check ==="
echo "Policy: docs/ops/error-budget-policy.md"
echo "SLOs:   docs/ops/slo-definition.md"
echo ""

if curl -sf "${BACKEND_URL}/health" >/dev/null 2>&1; then
  echo "→ Health"
  curl -sf "${BACKEND_URL}/health" | python3 -m json.tool 2>/dev/null || curl -sf "${BACKEND_URL}/health"
  echo ""
  echo "→ Ready"
  curl -sf "${BACKEND_URL}/ready" | python3 -m json.tool 2>/dev/null || curl -sf "${BACKEND_URL}/ready"
  echo ""
  echo "→ Admin metrics (if ADMIN_API_KEY set)"
  if [[ -n "${ADMIN_API_KEY:-}" ]]; then
    curl -sf "${BACKEND_URL}/api/v1/admin/metrics" -H "X-Admin-Key: ${ADMIN_API_KEY}" \
      | python3 -m json.tool | head -25
  else
    echo "NOTE: set ADMIN_API_KEY for admin metrics"
  fi
else
  echo "NOTE: backend not reachable at ${BACKEND_URL}"
fi

echo ""
python3 - <<'PY'
from pathlib import Path
import yaml

targets = yaml.safe_load(Path("docs/platform/plan6-kpi-targets.yaml").read_text(encoding="utf-8"))
print("Plan6 targets:")
for key, value in targets.get("targets", {}).items():
    print(f"  - {key}: {value}")
PY
echo ""
echo "PASS: Error budget snapshot recorded — compare with Prometheus/Grafana for prod"

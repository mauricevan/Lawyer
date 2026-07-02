#!/usr/bin/env bash
# Strategic risk review — register, regulatory radar, continuity (plan9 V).
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"
export PYTHONPATH=.

echo "=== Strategic risk review ==="

required=(
  docs/risk/strategic-risk-register.yaml
  docs/risk/vendor-model-risk.md
  docs/risk/regulatory-radar.yaml
  docs/risk/continuity-plan.md
  docs/risk/strategic-risk-report-template.md
)

for doc in "${required[@]}"; do
  [[ -f "$doc" ]] || { echo "FAIL: missing $doc"; exit 1; }
  echo "OK: $doc"
done

python3 - <<'PY'
from backend.src.services.strategic_risk_service import StrategicRiskService

service = StrategicRiskService()
errors = service.validate_register()
if errors:
    raise SystemExit(f"FAIL: {errors}")

high = service.high_risks()
print(f"OK: {len(service.load_register().get('risks', []))} risks registered")
print(f"OK: {len(high)} risks at or above escalation threshold")
for risk in high[:3]:
    print(f"  - {risk['id']}: exposure={risk['exposure']}")
PY

echo ""
echo "PASS: Strategic risk review succeeded."

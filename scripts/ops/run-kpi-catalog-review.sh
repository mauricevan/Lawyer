#!/usr/bin/env bash
# KPI catalog annual review — leading/lagging indicators (plan10 X).
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"
export PYTHONPATH=.

echo "=== KPI catalog review ==="

required=(
  docs/cycle/kpi-catalog.yaml
  docs/cycle/kpi-corrective-actions.md
  docs/cycle/org-retrospective-template.md
)

for doc in "${required[@]}"; do
  [[ -f "$doc" ]] || { echo "FAIL: missing $doc"; exit 1; }
  echo "OK: $doc"
done

python3 - <<'PY'
import json
from pathlib import Path

from backend.src.services.kpi_catalog_service import KpiCatalogService

service = KpiCatalogService()
errors = service.validate_catalog()
if errors:
    raise SystemExit(f"FAIL: {errors}")

leading = service.leading_indicators()
lagging = service.lagging_indicators()
print(f"OK: {len(leading)} leading, {len(lagging)} lagging indicators")

report = Path("docs/data/eval-reports/latest.json")
if report.is_file():
    data = json.loads(report.read_text(encoding="utf-8"))
    print(f"OK: eval report passed={data.get('passed')}")
else:
    print("NOTE: no eval report — run release eval")
PY

echo ""
echo "PASS: KPI catalog review succeeded."

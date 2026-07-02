#!/usr/bin/env bash
# Plan5 KPI snapshot — measurable gates + feedback SQL reminder (plan5 exit docs).
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"

echo "=== Plan5 KPI snapshot ==="
echo "Datum: $(date -Iseconds)"
echo "Scorecard: docs/product/plan5-kpi-scorecard.md"
echo ""

export PYTHONPATH=.
python3 - <<'PY'
from pathlib import Path
import yaml

data = yaml.safe_load(Path("docs/product/portfolio-metrics.yaml").read_text(encoding="utf-8"))
print(f"Quarter: {data.get('quarter', 'unknown')}")
print(f"Objectives: {len(data.get('objectives', []))}")
for item in data.get("objectives", []):
    print(f"  - {item['id']}: target={item['target']} source={item['source']}")
PY

echo ""
echo "→ Instrumentatie checks"
pytest backend/tests/test_portfolio_planning.py backend/tests/test_knowledge_base.py -q

BACKEND_URL="${BACKEND_URL:-http://127.0.0.1:8001}"
if curl -sf "${BACKEND_URL}/health" >/dev/null 2>&1; then
  echo ""
  echo "→ Runtime metrics (${BACKEND_URL})"
  curl -sf "${BACKEND_URL}/api/v1/admin/metrics" -H "X-Admin-Key: ${ADMIN_API_KEY:-}" 2>/dev/null \
    | python3 -m json.tool 2>/dev/null | head -30 \
    || echo "NOTE: admin metrics require ADMIN_API_KEY + auth"
else
  echo ""
  echo "NOTE: backend not reachable at ${BACKEND_URL}; skip live metrics"
fi

echo ""
echo "=== Manual KPI steps ==="
echo "1. ./scripts/qa/run-retrieval-eval.sh          # retrieval_quality"
echo "2. ./scripts/qa/run-domain-benchmark.sh      # domain_coverage"
echo "3. ./scripts/qa/run-multilingual-eval.sh       # multilingual_quality"
echo "4. Feedback SQL — see plan5-kpi-scorecard.md §4"
echo ""
echo "Update snapshot table in docs/product/plan5-kpi-scorecard.md §2 after measuring."

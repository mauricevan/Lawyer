#!/usr/bin/env bash
# Quarterly portfolio review — metrics, debt, and planning gates (plan5 J1).
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"
QUICK=false
if [[ "${1:-}" == "--quick" ]]; then
  QUICK=true
fi

echo "=== Quarterly portfolio review ==="

required_docs=(
  docs/product/portfolio-metrics.yaml
  docs/product/quarterly-roadmap.md
  docs/ops/capacity-model.md
  docs/ops/technical-debt-register.md
  docs/ops/architecture-review.md
  docs/engineering/onboarding.md
  docs/engineering/runbook-index.md
)

for doc in "${required_docs[@]}"; do
  if [[ ! -f "$doc" ]]; then
    echo "FAIL: missing $doc"
    exit 1
  fi
  echo "OK: $doc"
done

export PYTHONPATH=.
python3 - <<'PY'
import sys
from pathlib import Path
import yaml

path = Path("docs/product/portfolio-metrics.yaml")
data = yaml.safe_load(path.read_text(encoding="utf-8"))
objectives = data.get("objectives", [])
if len(objectives) < 5:
    sys.exit("FAIL: portfolio-metrics.yaml needs at least 5 objectives")
allocation = data.get("capacity_allocation", {})
for mode in ("healthy", "budget_burn"):
    buckets = allocation.get(mode, {})
    total = sum(buckets.values())
    if abs(total - 1.0) > 0.01:
        sys.exit(f"FAIL: {mode} allocation sums to {total}, expected 1.0")
print(f"OK: {len(objectives)} objectives, capacity allocation valid")
PY

if [[ "$QUICK" == true ]]; then
  echo ""
  echo "PASS: Quick portfolio review (docs + metrics schema)."
  exit 0
fi

echo ""
echo "→ Backend unit tests"
pytest backend/tests -m "not integration" -q

echo ""
echo "→ Recovery drill gate"
chmod +x scripts/ops/run-recovery-drill-gate.sh
CI=true ./scripts/ops/run-recovery-drill-gate.sh

echo ""
echo "→ Knowledge base check"
chmod +x scripts/ops/run-knowledge-base-check.sh
./scripts/ops/run-knowledge-base-check.sh

echo ""
echo "→ Portfolio planning tests"
pytest backend/tests/test_portfolio_planning.py backend/tests/test_knowledge_base.py -q

echo ""
echo "=== Review reminders ==="
echo "- Update technical-debt-register.md status"
echo "- Schedule architecture review (see docs/ops/architecture-review.md)"
echo "- Lock next quarter roadmap from docs/product/quarterly-roadmap.md"
echo ""
echo "PASS: Full quarterly portfolio review gates succeeded."

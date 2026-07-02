#!/usr/bin/env bash
# Sync quarterly capacity with portfolio metrics (plan8 Q).
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"

echo "=== Quarterly capacity sync ==="

required=(
  docs/product/portfolio-metrics.yaml
  docs/product/quarterly-roadmap.md
  docs/ops/capacity-model.md
)

for doc in "${required[@]}"; do
  [[ -f "$doc" ]] || { echo "FAIL: missing $doc"; exit 1; }
  echo "OK: $doc"
done

python3 - <<'PY'
from pathlib import Path
import yaml

metrics = yaml.safe_load(Path("docs/product/portfolio-metrics.yaml").read_text(encoding="utf-8"))
allocation = metrics.get("capacity_allocation", {})
healthy = allocation.get("healthy", {})
if not healthy:
    raise SystemExit("FAIL: portfolio-metrics missing capacity_allocation.healthy")
total = sum(healthy.values())
if abs(total - 1.0) > 0.01:
    raise SystemExit(f"FAIL: healthy allocation sums to {total}, expected 1.0")
print(f"OK: capacity_allocation healthy = {total}")

roadmap = Path("docs/product/quarterly-roadmap.md").read_text(encoding="utf-8")
if "debt" not in roadmap.lower():
    raise SystemExit("FAIL: quarterly-roadmap missing debt section")
print("OK: quarterly-roadmap references debt")
PY

chmod +x scripts/ops/run-quarterly-portfolio-review.sh 2>/dev/null || true
if [[ -x scripts/ops/run-quarterly-portfolio-review.sh ]]; then
  ./scripts/ops/run-quarterly-portfolio-review.sh --quick
fi

echo ""
echo "PASS: Quarterly capacity sync succeeded."

#!/usr/bin/env bash
# Portfolio board review — scoring, objectives, wind-down (plan9 T).
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"

echo "=== Portfolio board review ==="

required=(
  docs/product/portfolio-board-cadence.md
  docs/product/prioritization-model.yaml
  docs/product/non-strategic-winddown.md
  docs/product/portfolio-metrics.yaml
  docs/product/quarterly-roadmap.md
)

for doc in "${required[@]}"; do
  [[ -f "$doc" ]] || { echo "FAIL: missing $doc"; exit 1; }
  echo "OK: $doc"
done

export PYTHONPATH=.
python3 - <<'PY'
from pathlib import Path
import json
import yaml

from backend.src.services.portfolio_scoring_service import PortfolioScoringService

service = PortfolioScoringService()
sample = [
    {"id": "init-1", "impact": 5, "risk_reduction": 4, "effort": 3},
    {"id": "init-2", "impact": 2, "risk_reduction": 2, "effort": 5},
]
ranked = service.rank_initiatives(sample)
if not ranked[0]["schedule"]:
    raise SystemExit("FAIL: top initiative should schedule")
if ranked[-1]["schedule"]:
    raise SystemExit("FAIL: low initiative should wind down")

report = Path("docs/data/eval-reports/latest.json")
if report.is_file():
    data = json.loads(report.read_text(encoding="utf-8"))
    print(f"OK: latest eval passed={data.get('passed')}")
else:
    print("NOTE: no eval report yet — run release eval before board lock")

metrics = yaml.safe_load(Path("docs/product/portfolio-metrics.yaml").read_text(encoding="utf-8"))
print(f"OK: {len(metrics.get('objectives', []))} portfolio objectives")
PY

chmod +x scripts/ops/run-quarterly-portfolio-review.sh 2>/dev/null || true
./scripts/ops/run-quarterly-portfolio-review.sh --quick

echo ""
echo "PASS: Portfolio board review succeeded."

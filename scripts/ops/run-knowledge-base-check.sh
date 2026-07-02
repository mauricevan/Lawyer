#!/usr/bin/env bash
# Validate engineering knowledge base docs exist (plan5 J2).
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"

echo "=== Knowledge base check ==="

required=(
  docs/engineering/onboarding.md
  docs/product/plan5-kpi-scorecard.md
  docs/product/plan4-exit-gap.md
  docs/platform/self-service-ops.md
  docs/platform/env-parity-matrix.yaml
  docs/engineering/runbook-index.md
  docs/engineering/troubleshooting.md
  docs/engineering/pair-review-policy.md
  docs/engineering/incident-learnings.md
  docs/engineering/critical-components.yaml
  docs/data/dataset-changelog.md
  docs/data/data-lineage.md
  docs/data/eval-thresholds.yaml
  docs/data/prompt-change-control.md
  docs/data/experiment-policy.md
  docs/adr/README.md
  observability/runbooks/top-5-incidents.md
)

for doc in "${required[@]}"; do
  if [[ ! -f "$doc" ]]; then
    echo "FAIL: missing $doc"
    exit 1
  fi
  echo "OK: $doc"
done

python3 - <<'PY'
from pathlib import Path
import yaml

data = yaml.safe_load(Path("docs/engineering/critical-components.yaml").read_text(encoding="utf-8"))
components = data.get("components", [])
if len(components) < 4:
    raise SystemExit("FAIL: critical-components.yaml needs at least 4 components")
print(f"OK: {len(components)} critical components registered")
PY

echo ""
echo "PASS: Knowledge base check succeeded."

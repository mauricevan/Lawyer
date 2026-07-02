#!/usr/bin/env bash
# Validate enablement artifacts and onboarding KPI docs (plan8 S).
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"

echo "=== Enablement check ==="

required=(
  docs/engineering/playbooks/README.md
  docs/engineering/playbooks/first-contribution.md
  docs/engineering/playbooks/release.md
  docs/engineering/playbooks/incident-response.md
  docs/engineering/review-guild.md
  docs/engineering/onboarding-kpis.yaml
  docs/org/cross-team-escalation.md
)

for doc in "${required[@]}"; do
  [[ -f "$doc" ]] || { echo "FAIL: missing $doc"; exit 1; }
  echo "OK: $doc"
done

python3 - <<'PY'
from pathlib import Path
import yaml

kpis = yaml.safe_load(Path("docs/engineering/onboarding-kpis.yaml").read_text(encoding="utf-8"))
targets = kpis.get("targets", {})
if len(targets) < 3:
    raise SystemExit("FAIL: onboarding-kpis needs at least 3 targets")
print(f"OK: {len(targets)} onboarding KPI targets")

owners = yaml.safe_load(Path("docs/org/component-ownership-matrix.yaml").read_text(encoding="utf-8"))
if len(owners.get("components", [])) < 5:
    raise SystemExit("FAIL: ownership matrix needs at least 5 components")
print(f"OK: {len(owners['components'])} owned components")
PY

echo ""
echo "PASS: Enablement check succeeded."

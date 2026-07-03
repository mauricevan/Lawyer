#!/usr/bin/env bash
# Validate legal compliance artifacts: gaps, limitations, escalation (plan11 AC).
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"
export PYTHONPATH=.

echo "=== Legal compliance check ==="

required=(
  docs/legal/national-implementation-gaps.yaml
  docs/legal/national-implementation-gaps.md
  docs/legal/escalation-path.md
  docs/legal/product-limitations.md
  shared/config/product-limitations.yaml
)

for doc in "${required[@]}"; do
  [[ -f "$doc" ]] || { echo "FAIL: missing $doc"; exit 1; }
  echo "OK: $doc"
done

python3 - <<'PY'
from pathlib import Path
import yaml

escalation = Path("docs/legal/escalation-path.md").read_text(encoding="utf-8")
for heading in ("Wanneer escaleren", "Stappen", "SLA"):
    if heading not in escalation:
        raise SystemExit(f"FAIL: escalation-path.md missing section: {heading}")
print("OK: escalation-path.md sections")

gaps = yaml.safe_load(Path("docs/legal/national-implementation-gaps.yaml").read_text(encoding="utf-8"))
if len(gaps.get("jurisdictions", [])) < 4:
    raise SystemExit("FAIL: need at least 4 jurisdiction gaps documented")
print(f"OK: {len(gaps['jurisdictions'])} jurisdiction gaps")

limits = yaml.safe_load(Path("shared/config/product-limitations.yaml").read_text(encoding="utf-8"))
langs = limits.get("languages", {})
for code in ("nl", "en", "fr", "de", "es"):
    if code not in langs or len(langs[code]) < 3:
        raise SystemExit(f"FAIL: product-limitations missing bullets for {code}")
print(f"OK: product-limitations for {len(langs)} languages")
PY

pytest backend/tests/test_plan11_ac.py backend/tests/test_product_limitations.py -q
echo ""
echo "PASS: Legal compliance check succeeded."

#!/usr/bin/env bash
# Audit quality gates and release standards (plan8 R).
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"

echo "=== Quality gate audit ==="

required=(
  docs/engineering/definition-of-done.md
  docs/engineering/release-standards.md
  docs/engineering/quality-gates.yaml
  docs/org/component-ownership-matrix.yaml
  docs/org/interface-slas.yaml
)

for doc in "${required[@]}"; do
  [[ -f "$doc" ]] || { echo "FAIL: missing $doc"; exit 1; }
  echo "OK: $doc"
done

python3 - <<'PY'
import sys
from pathlib import Path
import yaml

gates = yaml.safe_load(Path("docs/engineering/quality-gates.yaml").read_text(encoding="utf-8"))
for gate_id, gate in gates.get("gates", {}).items():
    script = gate.get("script")
    if script and not Path(script).is_file():
        print(f"FAIL: gate {gate_id} missing script {script}")
        sys.exit(1)
    if script:
        print(f"OK: gate {gate_id} -> {script}")

ci = gates.get("ci_mapping", {})
workflow = Path(ci.get("workflow", ""))
if not workflow.is_file():
    print(f"FAIL: CI workflow missing {workflow}")
    sys.exit(1)
print(f"OK: CI workflow {workflow}")
PY

if [[ -x scripts/qa/run-integration-eval-gate.sh ]]; then
  echo "OK: integration eval script executable"
else
  echo "FAIL: run-integration-eval-gate.sh not executable"
  exit 1
fi

if [[ -x scripts/qa/run-release-eval-suite.sh ]]; then
  echo "OK: release eval script executable"
else
  echo "FAIL: run-release-eval-suite.sh not executable"
  exit 1
fi

if [[ -x scripts/qa/run-failover-eval.sh ]]; then
  echo "OK: failover eval script executable"
else
  echo "FAIL: run-failover-eval.sh not executable"
  exit 1
fi

if [[ -x scripts/ops/run-recovery-drill-gate.sh ]]; then
  echo "OK: recovery drill gate script executable"
else
  echo "FAIL: run-recovery-drill-gate.sh not executable"
  exit 1
fi

if [[ -x scripts/ops/run-incident-playbook-audit.sh ]]; then
  echo "OK: incident playbook audit script executable"
else
  echo "FAIL: run-incident-playbook-audit.sh not executable"
  exit 1
fi

if [[ -x scripts/platform/run-readiness-pass-rate-gate.sh ]]; then
  echo "OK: readiness pass-rate gate script executable"
else
  echo "FAIL: run-readiness-pass-rate-gate.sh not executable"
  exit 1
fi

if [[ -x scripts/platform/run-policy-registry-gate.sh ]]; then
  echo "OK: policy registry gate script executable"
else
  echo "FAIL: run-policy-registry-gate.sh not executable"
  exit 1
fi

echo ""
echo "PASS: Quality gate audit succeeded."

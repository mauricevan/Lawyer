#!/usr/bin/env bash
# Verify API input validation coverage meets plan4 E3 threshold.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"

PYTHONPATH=. python3 - <<'PY'
from backend.src.security.input_validation_audit import build_coverage_report, run_audit

report = build_coverage_report()
print(f"Input validation coverage: {report['coverage_percent']}% ({report['validated_endpoints']}/{report['total_endpoints']})")
run_audit(min_coverage=100.0)
print("Input validation audit passed.")
PY

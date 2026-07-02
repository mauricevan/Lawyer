#!/usr/bin/env bash
# Verify pair-review ACK when critical component paths change (plan5 J2).
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"
MODE="commit"
if [[ "${1:-}" == "--staged" ]]; then
  MODE="staged"
fi

if [[ "$MODE" == "staged" ]]; then
  CHANGED=$(git diff --cached --name-only)
else
  CHANGED=$(git diff --name-only HEAD~1 HEAD 2>/dev/null || true)
fi

export CHANGED_FILES="${CHANGED}"
export PAIR_REVIEW_ACK="${PAIR_REVIEW_ACK:-}"

python3 - <<'PY'
import os
import sys
from pathlib import Path

import yaml

changed = [line for line in os.environ.get("CHANGED_FILES", "").splitlines() if line.strip()]
if not changed:
    print("OK: no changed files to check.")
    sys.exit(0)

data = yaml.safe_load(
    Path("docs/engineering/critical-components.yaml").read_text(encoding="utf-8")
)
critical_paths: list[str] = []
for component in data.get("components", []):
    critical_paths.extend(component.get("paths", []))

hits: list[str] = []
for path in changed:
    for critical in critical_paths:
        if path == critical or path.startswith(critical.rstrip("/") + "/"):
            hits.append(path)
            break

if not hits:
    print("OK: no critical component paths changed.")
    sys.exit(0)

print("Critical paths changed:")
for hit in sorted(set(hits)):
    print(f"  - {hit}")

if os.environ.get("PAIR_REVIEW_ACK") == "yes":
    print("OK: PAIR_REVIEW_ACK=yes recorded.")
    sys.exit(0)

print("")
print("Complete pair review: docs/engineering/pair-review-policy.md")
print("Re-run with: PAIR_REVIEW_ACK=yes ./scripts/ops/check-pair-review.sh")
sys.exit(1)
PY

#!/usr/bin/env bash
# Automated release gates — run before production deploy.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"

echo "=== Release checklist: automated gates ==="

chmod +x scripts/security/check-secrets.sh \
  scripts/security/check-log-output.sh \
  scripts/security/run-input-validation-audit.sh

./scripts/security/check-secrets.sh all
./scripts/security/check-log-output.sh
./scripts/security/run-input-validation-audit.sh

echo "→ Lifecycle eval gate"
chmod +x scripts/platform/run-lifecycle-eval-gate.sh \
  scripts/platform/run-deprecation-register-check.sh
./scripts/platform/run-lifecycle-eval-gate.sh

echo "→ Backend unit tests"
pytest backend/tests -m "not integration" -q

echo "→ Frontend unit tests"
(cd frontend && npm test -- --run)

echo "→ Knowledge base check"
chmod +x scripts/ops/run-knowledge-base-check.sh scripts/ops/check-pair-review.sh
./scripts/ops/run-knowledge-base-check.sh

if ! PAIR_REVIEW_ACK="${PAIR_REVIEW_ACK:-}" ./scripts/ops/check-pair-review.sh; then
  if [[ "${PAIR_REVIEW_ACK:-}" == "yes" ]]; then
  echo "WARN: pair review ACK set but critical paths changed — ensure checklist completed"
  else
    echo "NOTE: critical paths changed; set PAIR_REVIEW_ACK=yes after pair review if intentional"
  fi
fi

echo ""
echo "PASS: All automated release gates succeeded."
echo "Manual steps: see docs/ops/release-checklist.md"

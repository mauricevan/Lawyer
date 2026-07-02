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

echo "→ Backend unit tests"
pytest backend/tests -m "not integration" -q

echo "→ Frontend unit tests"
(cd frontend && npm test -- --run)

echo ""
echo "PASS: All automated release gates succeeded."
echo "Manual steps: see docs/ops/release-checklist.md"

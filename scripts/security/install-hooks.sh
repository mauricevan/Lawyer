#!/usr/bin/env bash
# Install repository git hooks (pre-commit secret scan).
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"

chmod +x .githooks/pre-commit scripts/security/check-secrets.sh
git config core.hooksPath .githooks

echo "Git hooks installed: core.hooksPath=.githooks"

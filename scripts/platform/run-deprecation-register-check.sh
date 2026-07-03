#!/usr/bin/env bash
# Validate deprecation register covers no_go domain seeds (plan13 AC).
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"
export PYTHONPATH=.

python3 backend/scripts/validate_deprecation_register.py

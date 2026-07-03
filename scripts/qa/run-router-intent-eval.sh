#!/usr/bin/env bash
# Router intent library eval — offline, no stack required (plan12 AC).
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"
export PYTHONPATH=.

python3 backend/scripts/run_router_intent_eval.py "$@"

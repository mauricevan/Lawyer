#!/usr/bin/env bash
# EXP-002 reranker A/B eval — requires Qdrant + seeded corpus (plan12 AA).
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"
export PYTHONPATH=.

FIXTURE="${FIXTURE:-backend/tests/fixtures/rag_eval_questions.json}"
ARGS=(--fixture "$FIXTURE")

python3 backend/scripts/run_reranker_ab_eval.py "${ARGS[@]}"
echo "→ Report: docs/data/eval-reports/reranker-ab-latest.json"

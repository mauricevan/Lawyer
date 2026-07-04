#!/usr/bin/env bash
# EU jurisprudence maturity gate — RAG path must work without per-question topic fixes.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"
export PYTHONPATH=.

echo "== Unit tests (planner, extractive, maturity, discovery, agent) =="
python3 -m pytest \
  backend/tests/test_legal_planner_scoring.py \
  backend/tests/test_consumer_withdrawal_period.py \
  backend/tests/test_gdpr_lawful_basis_professional.py \
  backend/tests/test_retrieval_live_fallback.py \
  backend/tests/test_legal_source_planner_service.py \
  backend/tests/test_celex_discovery_service.py \
  backend/tests/test_celex_hint_resolver_discovery.py \
  backend/tests/test_legal_extractive_generic_obligations.py \
  backend/tests/test_environmental_liability.py \
  backend/tests/test_sparql_celex_discovery.py \
  backend/tests/test_curated_celex_property.py \
  backend/tests/test_llm_legal_planner_service.py \
  backend/tests/test_instrument_resolver_service.py \
  backend/tests/test_article_fetch_orchestrator.py \
  backend/tests/test_citation_verifier_service.py \
  backend/tests/test_live_chunk_builder.py \
  -q -m "not integration"

API_URL="${API_URL:-http://localhost:8003}"
if ! curl -sf "${API_URL}/health" >/dev/null 2>&1; then
  echo "ERROR: backend not reachable at ${API_URL}"
  exit 1
fi

echo "== EUR-Lex breadth smoke =="
node "$ROOT/scripts/qa/eurlex-breadth-smoke.mjs" "$API_URL"

echo "== Maturity RAG audit (no topic dependency) =="
node "$ROOT/scripts/qa/maturity-rag-audit.mjs" "$API_URL"

echo "== Agent flow smoke =="
node "$ROOT/scripts/qa/agent-flow-smoke.mjs" "$API_URL"

echo "== Novel layperson audit =="
node "$ROOT/scripts/qa/layperson-novel-audit.mjs" "$API_URL"

echo "Maturity gate OK"

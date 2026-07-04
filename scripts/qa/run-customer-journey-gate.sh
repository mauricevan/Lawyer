#!/usr/bin/env bash
# Customer journey regression gate — blocks release on layperson path regressions.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"
export PYTHONPATH=.

echo "== Customer journey regression tests =="
python3 -m pytest backend/tests/test_customer_journey_regression.py -q
python3 -m pytest backend/tests/test_question_intent_service.py \
  backend/tests/test_article_specific_pipeline.py \
  backend/tests/test_layperson_topic_regression.py \
  backend/tests/test_blueprint_showcase.py \
  backend/tests/test_legal_source_planner_service.py \
  backend/tests/test_legal_planner_domain_registry.py \
  backend/tests/test_legal_extractive_decision.py \
  backend/tests/test_fictional_question_guard.py \
  backend/tests/test_eu_conformity_declaration.py \
  backend/tests/test_webshop_regels_overview.py \
  backend/tests/test_retrieval_live_fallback.py \
  backend/tests/test_gdpr_lawful_basis_professional.py \
  backend/tests/test_consumer_withdrawal_period.py \
  backend/tests/test_legal_planner_scoring.py -q -m "not integration"
python3 -m pytest \
  backend/tests/test_context_adequacy_service.py \
  backend/tests/test_vague_question_service.py \
  backend/tests/test_rag_coverage_gap.py \
  backend/tests/test_insufficient_coverage_answer_service.py \
  backend/tests/test_layperson_answer_formatter.py \
  backend/tests/test_layperson_answer_service.py \
  backend/tests/test_layperson_topic_service.py \
  backend/tests/test_layperson_topic_bundle.py \
  backend/tests/test_question_chunk_relevance.py \
  backend/tests/test_article_utils.py \
  backend/tests/test_coverage_guidance_yaml.py \
  backend/tests/test_answer_text_sanitizer.py \
  -q

if command -v node >/dev/null 2>&1; then
  API_URL="${API_URL:-http://localhost:8003}"
  if curl -sf "${API_URL}/health" >/dev/null 2>&1; then
    echo "== Layperson clarity audit (≥14/20 GOED) =="
    node "$ROOT/scripts/qa/layperson-clarity-audit.mjs" "$API_URL"
    echo "== Novel layperson audit (≥18/18 GOED) =="
    node "$ROOT/scripts/qa/layperson-novel-audit.mjs" "$API_URL"
    echo "== Fresh layperson audit (≥13/18 GOED) =="
    node "$ROOT/scripts/qa/layperson-fresh-audit.mjs" "$API_URL"
    echo "== W-set layperson audit (≥70% GOED) =="
    node "$ROOT/scripts/qa/layperson-w-audit.mjs" "$API_URL"
    echo "== Article-specific audit (system instruction §7.4) =="
    node "$ROOT/scripts/qa/article-specific-audit.mjs" "$API_URL"
    echo "== Maturity RAG audit (≥12/12, no topic dependency) =="
    node "$ROOT/scripts/qa/maturity-rag-audit.mjs" "$API_URL"
    echo "== EUR-Lex breadth smoke =="
    node "$ROOT/scripts/qa/eurlex-breadth-smoke.mjs" "$API_URL"
  else
    echo "WARN: backend not reachable at ${API_URL}; skip layperson-clarity-audit"
  fi
fi

echo "== Prompt injection guard =="
python3 -m pytest backend/tests/test_query_api_e2e.py::test_query_rejects_injection -q

if [[ -x "$ROOT/scripts/qa/run-legal-compliance-check.sh" ]]; then
  echo "== Legal compliance check =="
  "$ROOT/scripts/qa/run-legal-compliance-check.sh"
fi

echo "Customer journey gate: OK"

if [[ "${1:-}" == "--smoke-live" ]]; then
  echo "== Docker local smoke =="
  "$ROOT/scripts/qa/smoke-docker-local.sh"
fi

if [[ "${1:-}" == "--smoke-live" ]] && command -v node >/dev/null 2>&1; then
  echo "== Mobile a11y smoke =="
  node "$ROOT/scripts/demo/mobile-a11y-smoke.mjs" || echo "WARN: mobile a11y smoke skipped (frontend down?)"
fi

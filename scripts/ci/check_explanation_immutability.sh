#!/usr/bin/env bash
# CI guard: explanation engine must not mutate answers post-compose in pipeline.
set -euo pipefail

PIPELINE="backend/src/services/agent_v4_pipeline_service.py"
FAIL=0

check_zero() {
  local pattern="$1"
  local label="$2"
  local count
  count=$(rg -c "$pattern" "$PIPELINE" 2>/dev/null || true)
  count="${count:-0}"
  if [[ "$count" != "0" ]]; then
    echo "FAIL: $label ($count matches in $PIPELINE)"
    rg "$pattern" "$PIPELINE" || true
    FAIL=1
  else
    echo "OK: $label"
  fi
}

check_zero '\.revise\(' 'no .revise() in pipeline'
check_zero 'RevisionService' 'no RevisionService in pipeline'
check_zero 'LegalJudgeGateService|CaseLawSimulationGateService|MultiJudgeGateService|DoctrineEvolutionGateService|DoctrineAnchoringGateService|DoctrineStabilityGateService' 'no simulation GateService in pipeline'
check_zero '_inject_ilcl' 'no _inject_ilcl in pipeline'
check_zero 'judge_gate|court_gate|panel_gate|doctrine_gate' 'no simulation gates in pipeline'

RENDERER="backend/src/services/explanation_renderer_service.py"
if rg -q 'from backend\.src\.services\.|from backend\.src\.services import|LlmService|llm_service' "$RENDERER" 2>/dev/null; then
  echo "FAIL: renderer imports services or LLM"
  FAIL=1
else
  echo "OK: renderer purity"
fi

if [[ "$FAIL" -ne 0 ]]; then
  exit 1
fi
echo "All explanation immutability checks passed."

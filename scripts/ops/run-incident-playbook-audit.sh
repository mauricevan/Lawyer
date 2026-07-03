#!/usr/bin/env bash
# Tier-1 alert runbook + incident playbook audit (plan14 AD).
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"
export PYTHONPATH=.

python3 backend/scripts/run_incident_playbook_audit.py "$@"
echo "→ Report: docs/data/reliability-reports/incident-playbook-audit-latest.json"
echo "PASS: Incident playbook audit succeeded"

#!/usr/bin/env bash
# Provision local test data: corpus + eval fixtures (plan6 M2).
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"
export PYTHONPATH=.

echo "=== Provision test data ==="
python3 ingestion/scripts/seed_corpus.py
python3 backend/scripts/build_eval_fixture.py
python3 backend/scripts/build_multilingual_eval_fixture.py
echo "PASS: Test data provisioned"

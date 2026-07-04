#!/usr/bin/env bash
# Ingest Priority-1 EU corpus documents for full product promise coverage.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"
export PYTHONPATH=.

ALL_CURATED=false
while [[ $# -gt 0 ]]; do
  case "$1" in
    --all-curated) ALL_CURATED=true; shift ;;
    *) echo "Unknown option: $1"; exit 1 ;;
  esac
done

PRIORITY_CELEX=(
  "32013R0952"
  "32016R0679"
  "32011L0083"
  "32004R0261"
  "32024R1689"
  "32022R2065"
  "32022R1925"
  "32023R1114"
  "32022R2554"
  "32022L2555"
  "32024L1385"
  "32019L1152"
  "32019L0771"
  "32023R0988"
  "31987R2658"
  "32004L0035"
)

if [[ "$ALL_CURATED" == "true" ]]; then
  echo "== Full curated corpus ingest =="
  python3 ingestion/scripts/ingest_curated.py --skip-existing --delay-seconds 2
  echo "Done."
  exit 0
fi

echo "== Priority-1 corpus ingest (${#PRIORITY_CELEX[@]} documents) =="
for celex in "${PRIORITY_CELEX[@]}"; do
  echo "→ $celex"
  python3 ingestion/scripts/ingest_curated.py \
    --from-celex "$celex" --skip-existing --delay-seconds 2
done
echo "Done."

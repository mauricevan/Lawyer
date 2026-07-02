#!/usr/bin/env bash
# Warm retrieval cache with priority eval questions (plan6 K2).
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"

BACKEND_URL="${BACKEND_URL:-http://127.0.0.1:8001}"
FIXTURE="${FIXTURE:-backend/tests/fixtures/rag_eval_questions.json}"
MAX="${MAX:-10}"

if [[ ! -f "$FIXTURE" ]]; then
  echo "FAIL: fixture not found: $FIXTURE"
  exit 1
fi

echo "=== Cache warmup (${BACKEND_URL}, max ${MAX}) ==="
python3 - <<'PY' "$FIXTURE" "$BACKEND_URL" "$MAX"
import json
import sys
import urllib.request

fixture, base_url, max_raw = sys.argv[1:4]
max_count = int(max_raw)
items = json.loads(open(fixture, encoding="utf-8").read())[:max_count]
warmed = 0
for item in items:
    payload = json.dumps({"question": item["question"], "language": "nl", "audience": "professional"}).encode()
    req = urllib.request.Request(
        f"{base_url.rstrip('/')}/api/v1/query",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            if response.status == 200:
                warmed += 1
    except Exception as exc:
        print(f"WARN: warmup failed for question: {exc}")
print(f"Warmed {warmed}/{len(items)} queries")
if warmed == 0:
    raise SystemExit("FAIL: no queries warmed — is backend running?")
PY
echo "PASS: Cache warmup complete"

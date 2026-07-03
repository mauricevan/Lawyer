#!/usr/bin/env bash
# Stack-aware release eval: full suite when infra is up (plan11 AD).
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"
export PYTHONPATH=.

REQUIRED=false
for arg in "$@"; do
  case "$arg" in
    --required) REQUIRED=true ;;
  esac
done

chmod +x scripts/qa/check-eval-stack.sh scripts/qa/run-release-eval-suite.sh
chmod +x scripts/qa/run-integration-eval-gate.sh

if ! ./scripts/qa/check-eval-stack.sh >/dev/null 2>&1; then
  if [[ "$REQUIRED" == true ]]; then
    echo "FAIL: eval stack not ready (Qdrant + Postgres required)"
    exit 1
  fi
  echo "SKIP: eval stack not ready"
  exit 0
fi

CHUNK_COUNT="$(PYTHONPATH=. python3 - <<'PY'
import asyncio
from sqlalchemy import text
from backend.src.database import SessionLocal

async def main() -> None:
    async with SessionLocal() as session:
        result = await session.execute(text("SELECT COUNT(*) FROM chunks"))
        print(result.scalar() or 0)

asyncio.run(main())
PY
)"

if [[ "${CHUNK_COUNT:-0}" -ge 50 ]]; then
  echo "→ Stack ready (${CHUNK_COUNT} chunks) — full release eval suite"
  ./scripts/qa/run-release-eval-suite.sh
else
  echo "→ Stack ready (${CHUNK_COUNT} chunks) — CI integration eval gate"
  ./scripts/qa/run-integration-eval-gate.sh
fi

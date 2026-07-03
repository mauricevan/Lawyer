#!/usr/bin/env bash
# Verify Qdrant and Postgres are reachable for integration eval (plan11 AD).
set -euo pipefail

QDRANT_URL="${QDRANT_URL:-http://localhost:6333}"
DATABASE_URL="${DATABASE_URL:-postgresql+asyncpg://lawyer:lawyer_dev@localhost:5432/lawyer}"

check_qdrant() {
  curl -sf "${QDRANT_URL}/collections" >/dev/null 2>&1
}

check_postgres() {
  PYTHONPATH=. python3 - <<'PY'
import asyncio
import os
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

async def main() -> None:
    engine = create_async_engine(os.environ["DATABASE_URL"])
    async with engine.connect() as conn:
        await conn.execute(text("SELECT 1"))
    await engine.dispose()

asyncio.run(main())
PY
}

if check_qdrant && check_postgres; then
  echo "STACK_READY"
  exit 0
fi
echo "STACK_NOT_READY"
exit 1

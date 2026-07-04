#!/usr/bin/env bash
set -euo pipefail

cd /app/backend
alembic upgrade head
cd /app

exec uvicorn backend.src.main:app --host 0.0.0.0 --port 8000 --reload

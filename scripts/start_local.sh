#!/usr/bin/env bash
# Start EUR-Lex RAG stack locally (no Docker/sudo required)
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
export PG_BIN="$ROOT/tools/pg_extract/usr/lib/postgresql/16/bin"
export LD_LIBRARY_PATH="$ROOT/tools/pg_extract/usr/lib/x86_64-linux-gnu:${LD_LIBRARY_PATH:-}"
export PGDATA="$ROOT/data/postgres"
export PYTHONPATH="$ROOT"

mkdir -p "$ROOT/data/qdrant_storage" "$ROOT/data/postgres"

start_postgres() {
  if "$PG_BIN/pg_isready" -h localhost -p 5432 >/dev/null 2>&1; then
    echo "PostgreSQL already running"
    return
  fi
  if [ ! -f "$PGDATA/PG_VERSION" ]; then
    "$PG_BIN/initdb" -D "$PGDATA" -U lawyer --auth-local=trust --auth-host=trust
    sed -i "s|#listen_addresses = 'localhost'|listen_addresses = 'localhost'|" "$PGDATA/postgresql.conf"
    sed -i "s|#unix_socket_directories = '/var/run/postgresql'|unix_socket_directories = '$PGDATA'|" "$PGDATA/postgresql.conf"
  fi
  "$PG_BIN/pg_ctl" -D "$PGDATA" -l "$PGDATA/logfile" start
  sleep 2
  "$PG_BIN/createdb" -h localhost -U lawyer lawyer 2>/dev/null || true
  echo "PostgreSQL started"
}

start_qdrant() {
  if curl -sf http://localhost:6333/healthz >/dev/null 2>&1; then
    echo "Qdrant already running"
    return
  fi
  nohup "$ROOT/tools/qdrant" --config-path "$ROOT/tools/qdrant_config.yaml" \
    > "$ROOT/data/qdrant.log" 2>&1 &
  sleep 2
  echo "Qdrant started"
}

case "${1:-all}" in
  postgres) start_postgres ;;
  qdrant) start_qdrant ;;
  seed)
    start_postgres
    start_qdrant
    python3 "$ROOT/ingestion/scripts/seed_corpus.py"
    ;;
  backend)
    cd "$ROOT" && uvicorn backend.src.main:app --host 0.0.0.0 --port 8000
    ;;
  frontend)
    cd "$ROOT/frontend" && npm run dev -- --hostname 0.0.0.0 --port 3000
    ;;
  all)
    start_postgres
    start_qdrant
    echo "Stack ready. Run in separate terminals:"
    echo "  $0 backend"
    echo "  $0 frontend"
    ;;
  *)
    echo "Usage: $0 {postgres|qdrant|seed|backend|frontend|all}"
    exit 1
    ;;
esac

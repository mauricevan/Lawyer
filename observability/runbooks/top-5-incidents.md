# Lawyer RAG — Top 5 incident runbooks

## 1. Backend down / `/ready` degraded

**Symptoms:** 5xx on `/api/v1/query`, Prometheus alert `LawyerBackendDown`.

**Steps:**
1. Check `curl http://localhost:8001/ready` (or container `backend:8000/ready`).
2. Inspect `docker compose logs backend --tail 100`.
3. Verify Postgres, Redis, Qdrant checks in `/ready` response.
4. Restart: `docker compose restart backend`.
5. If DB migration issue: `cd backend && alembic upgrade head`.

## 2. Live fallback failures

**Symptoms:** Alert `LawyerHighFallbackFailureRate`, empty citations, `lawyer_fallback_success_total` flat.

**Steps:**
1. Confirm EUR-Lex/SPARQL reachability from backend container.
2. Temporarily disable: `./scripts/ops/rollback-features.sh`.
3. Check logs for `429`/`503` in `live_retrieval_service`.
4. Lower traffic or increase `LIVE_FALLBACK_TIMEOUT_SECONDS` if timeouts dominate.

## 3. Cache miss storm / high latency

**Symptoms:** High query latency, `lawyer_cache_hits_total` not growing.

**Steps:**
1. Check Redis: `GET /api/v1/admin/cache`.
2. Verify `ENABLE_REDIS_CACHE=true` and Redis healthy.
3. Purge expired rows: `POST /api/v1/admin/cache/cleanup`.
4. Warm critical queries manually if needed.

## 4. Ingest enqueue failures

**Symptoms:** Alert `LawyerIngestEnqueueFailures`, auto-upgrade not progressing.

**Steps:**
1. Check `celery-worker` logs: `docker compose logs celery-worker`.
2. Verify `ENABLE_CELERY_INGEST=true` and Redis broker URL.
3. Inspect `/api/v1/admin/ingestion-jobs` for stuck `pending`/`failed`.
4. Disable auto-upgrade via rollback script if queue is overloaded.

## 5. PostgreSQL unavailable

**Symptoms:** `/ready` shows `postgres: error`, audit/cache writes fail.

**Steps:**
1. Check local/container Postgres: `docker compose ps postgres`.
2. If host port conflict, use `docker-compose.local.yml`.
3. Restore from backup per environment policy.
4. Run `alembic upgrade head` after restore.

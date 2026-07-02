# EUR-Lex RAG Platform

EU juridisch onderzoeksplatform met RAG (Retrieval-Augmented Generation) over EUR-Lex/CELLAR data.

## Stack

- **Backend:** Python 3.12, FastAPI, PostgreSQL, Qdrant
- **Frontend:** Next.js 15, TypeScript
- **LLM:** Google Gemma 4 31B (free) via [OpenRouter](https://openrouter.ai/google/gemma-4-31b-it:free) — fallback: Claude (Anthropic)
- **Embeddings:** multilingual-e5-large (lokaal) of OpenAI

## Quick start

```bash
cp .env.example .env
docker compose up -d postgres qdrant
pip install -r backend/requirements.txt -r ingestion/requirements.txt
PYTHONPATH=. python ingestion/scripts/seed_corpus.py
uvicorn backend.src.main:app --reload --port 8000
cd frontend && npm install && npm run dev
```

## Secret hygiene

- Gebruik alleen placeholders in `.env.example`; zet nooit echte secrets in git.
- Houd `.env` lokaal en deel het niet via commits, screenshots of terminal dumps.
- Volledige inventaris en rotatie: [`docs/security/`](docs/security/).
- Na mogelijke blootstelling: volg [`incident-key-exposure.md`](docs/security/incident-key-exposure.md).

```bash
# Eenmalig: pre-commit hook activeren
./scripts/security/install-hooks.sh

# Handmatig scannen
./scripts/security/check-secrets.sh all
./scripts/security/check-log-output.sh
./scripts/security/run-rotation-tabletop.sh
```

- Frontend: http://localhost:3000
- API: http://localhost:8000/docs
- Prometheus: http://localhost:9090
- Grafana: http://localhost:3001 (`admin` / `sloten` lokaal; override via `GRAFANA_ADMIN_PASSWORD`)

## Observability

Met de volledige stack draaien metrics en dashboards automatisch mee:

```bash
docker compose up -d backend prometheus grafana celery-worker
```

Als poort `5432` al door lokale PostgreSQL wordt gebruikt:

```bash
docker compose -f docker-compose.yml -f docker-compose.local.yml up -d
```

Verificatie:

```bash
BACKEND_URL=http://127.0.0.1:8001 ./scripts/observability/verify-stack.sh
```

- Backend exposeert Prometheus metrics op `GET /metrics`
- Prometheus scrapet `backend:8000` (zie `observability/prometheus/prometheus.yml`)
- Grafana laadt datasource + dashboard `Lawyer RAG Overview` uit `observability/grafana/`
- Basis alerts staan in `observability/prometheus/alerts.yml` (backend down, fallback failures, ingest enqueue failures)

## Schaal (plan3)

```bash
# Load test (backend moet draaien)
python3 scripts/qa/loadtest_queries.py --url http://127.0.0.1:8001/api/v1/query --requests 20

# Celery workers: high-priority + batch queue
docker compose up -d celery-worker celery-worker-batch
```

```bash
docker compose -f docker-compose.yml -f docker-compose.scale.yml up -d
```

## Tests

```bash
PYTHONPATH=. pytest backend/tests -v -m "not integration"
```

Database migraties:

```bash
cd backend && alembic upgrade head
```

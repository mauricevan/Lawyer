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

```bash
./scripts/observability/verify-stack.sh
```

## Release governance

```bash
./scripts/ops/run-release-checklist.sh   # vóór productie-deploy
./scripts/ops/run-hotfix-rollback.sh     # incident mitigatie
```

Zie `docs/ops/` voor checklist, SLO's, escalatie en hotfix-runbooks.  
Nieuwe engineers: start bij [`docs/engineering/onboarding.md`](docs/engineering/onboarding.md).  
Platform scripts: [`docs/platform/self-service-ops.md`](docs/platform/self-service-ops.md).

## Project status

**PRODUCTION READY** (plan31 complete, 2026-07-03)

```bash
./scripts/ops/run-project-completion-gate.sh   # volledige productie-gate
```

Zie [`docs/cycle/project-completion.md`](docs/cycle/project-completion.md).

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
./scripts/qa/smoke-docker-local.sh
```

### Omgeving → poort → env var

| Omgeving | Frontend | Backend API | Env var |
|---|---|---|---|
| `docker compose up` | http://localhost:3000 | http://localhost:8000 | `NEXT_PUBLIC_API_URL=http://localhost:8000` |
| `docker compose.local.yml` | http://localhost:3000 | http://localhost:8001 | `NEXT_PUBLIC_API_URL=http://localhost:8001` |
| Frontend dev (lokaal) | http://localhost:3000 | http://localhost:8001 | `frontend/.env.local` — **herstart** na wijziging |

Backend-container draait migraties automatisch via `docker/entrypoint-backend.sh` (`alembic upgrade head`).

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

### EU-brede dekking (willekeurige richtlijnvragen)

Voor betrouwbare antwoorden op willekeurige EU-wetvragen:

1. **Backend** met `ENABLE_LIVE_FALLBACK=true` (standaard) — live EUR-Lex wanneer de corpus mist
2. **CELEX-discovery** — titelindex + SPARQL (`ingestion/data/celex_title_index.json`, bouw met `python ingestion/scripts/build_celex_title_index.py`)
3. **Qdrant** (aanbevolen) — lagere latency; start met `docker compose up -d qdrant`
4. **Corpus ingest** — priority: `bash scripts/ingest/ingest-priority-corpora.sh` of volledig: `bash scripts/ingest/ingest-priority-corpora.sh --all-curated`
5. **Maturity gate** — `API_URL=http://localhost:8003 bash scripts/qa/run-maturity-gate.sh`

Zonder live fallback of corpus blijven onbekende richtlijnen een gap — dat is verwacht gedrag binnen EU-only scope.

Database migraties:

```bash
cd backend && alembic upgrade head
```

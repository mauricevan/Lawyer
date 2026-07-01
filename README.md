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

- Frontend: http://localhost:3000
- API: http://localhost:8000/docs

## Schaal (fase 4+)

```bash
docker compose -f docker-compose.yml -f docker-compose.scale.yml up -d
```

## Tests

```bash
PYTHONPATH=. pytest backend/tests -v
```

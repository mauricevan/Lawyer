# Data lineage (plan7 N)

```
curated_celex.yaml
    → ingest_curated.py / seed_corpus.py
    → CellarRestClient (EUR-Lex)
    → LegalChunker + ChunkMetadataValidator
    → PostgreSQL (documents, chunks, FTS)
    → Qdrant (vectors)

User query
    → QueryRouterService (language, domain)
    → RagService (hybrid RRF / cache / live_fallback)
    → live_cache + redis (cache upgrade path)
    → LlmService (prompts.yaml v1)

Eval fixtures
    → run_eval_suite.py
    → eval_baseline.json (regression compare)
    → docs/data/eval-reports/latest.json
```

## Cache-upgrade pad

1. Local/Qdrant miss → live EUR-Lex fetch
2. Chunks opgeslagen in `live_cache` (Postgres)
3. Redis query cache (`query_cache_service`)
4. Optioneel: auto-upgrade queue (Celery) → permanente index

## Traceerbaarheid

| Stap | Registry key | Audit |
|---|---|---|
| Seed ingest | `curated_corpus` | ingest logs + `indexed_at` |
| Eval run | `eval_questions_*` | eval report JSON |
| Prompt wijziging | `prompts` v in shared/config | git + change control |
| Retrieval params | `retrieval_params.yaml` | env + registry version |

Bron: [dataset_registry.yaml](../../ingestion/src/data/dataset_registry.yaml)

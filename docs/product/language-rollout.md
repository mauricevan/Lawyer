# Taaluitrol FR/DE/ES (plan5 I2)

## Geactiveerde talen

| Code | Status | FTS | CELLAR | Fallback |
|---|---|---|---|---|
| nl | go | dutch | NLD | en |
| en | go | english | ENG | — |
| fr | go | french | FRA | en |
| de | go | german | DEU | en |
| es | go | spanish | SPA | en |

Bron: `ingestion/src/data/language_registry.yaml`

## Detectie

- Backend: `LanguageDetectionService` (stopwoord-scoring)
- `auto` in API-request → detectie op vraagtekst
- Expliciete taal → gebruikt indien `status: go`

## Fallback-paden

1. **PostgreSQL FTS** — taalspecifieke `ts_config`, anders `simple`
2. **Qdrant retrieval** — gevraagde taal → registry chain → `nl` corpus-fallback
3. **SPARQL/EUR-Lex** — gevraagde taal → `fallback_chain` (meestal `en`)
4. **Live retrieval** — probeert elke taal in de chain tot HTML beschikbaar is

Zie: [language-fallback-matrix.md](./language-fallback-matrix.md)

## Validatie

```bash
./scripts/qa/run-ingest-multilingual-seed.sh    # native FR/DE/ES corpus (EXP-001)
PYTHONPATH=. python3 backend/scripts/build_multilingual_eval_fixture.py
./scripts/qa/run-multilingual-eval.sh
```

Drempel per taal: Recall@5 ≥ 0.85 (native corpus, `eval-thresholds.yaml`).

Stub-reindex (bijv. AI Act FR na eerdere partial ingest):

```bash
PYTHONPATH=. python3 ingestion/scripts/ingest_multilingual_seed.py \
  --languages fr --celex 32024R1689 --force-reindex
```

Vóór eerste ingest: `cd backend && PYTHONPATH=.. alembic upgrade head` (chunks.text + FTS).

## UI

- Taalkiezer op homepage (`auto`, nl, en, fr, de, es)
- Disclaimers gelokaliseerd via `shared/legal/disclaimers.py` + frontend mirror

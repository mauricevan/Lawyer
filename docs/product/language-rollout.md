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
2. **SPARQL/EUR-Lex** — gevraagde taal → `fallback_chain` (meestal `en`)
3. **Live retrieval** — probeert elke taal in de chain tot HTML beschikbaar is

Zie: [language-fallback-matrix.md](./language-fallback-matrix.md)

## Validatie

```bash
PYTHONPATH=. python3 backend/scripts/build_multilingual_eval_fixture.py
./scripts/qa/run-multilingual-eval.sh
```

Drempel per taal: Recall@5 ≥ 0.70 (pilotfase).

## UI

- Taalkiezer op homepage (`auto`, nl, en, fr, de, es)
- Disclaimers gelokaliseerd via `shared/legal/disclaimers.py` + frontend mirror

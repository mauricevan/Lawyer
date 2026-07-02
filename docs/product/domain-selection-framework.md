# Domein-selectiekader (plan5 I1)

## Criteria

| Criterium | Schaal | Gewicht |
|---|---|---|
| **Vraagvolume** | low / medium / high | 30% |
| **Risico** (fout antwoord = schade) | low / medium / high | 35% |
| **Impact** (strategische waarde) | low / medium / high | 35% |

## Beslisregels

| Status | Betekenis | Actie |
|---|---|---|
| **go** | Productie-klaar | Domein actief in router + UI-filter |
| **pilot** | Beperkte seedset | Alleen met disclaimer; benchmark monitoren |
| **no_go** | Niet vrijgegeven | Router mag hinten, geen productbelofte |

## Bron van waarheid

- Registry: `ingestion/src/data/domain_registry.yaml`
- Loader: `ingestion/src/data/domain_registry_loader.py`
- Benchmark: `./scripts/qa/run-domain-benchmark.sh`

## Minimale drempels

| Status | Recall@5 |
|---|---|
| go | ≥ 0.75–0.80 (per domein in registry) |
| pilot | ≥ 0.70 |
| no_go | geen productie-release |

Zie ook: [domain-go-no-go.md](./domain-go-no-go.md)

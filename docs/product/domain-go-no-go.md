# Domein go/no-go — huidige beslissingen

Laatste evaluatie: draai `./scripts/qa/run-domain-benchmark.sh` na re-index.

| Domein | Status | Cluster | Drempel Recall@5 |
|---|---|---|---|
| ai | go | ai_digital | 0.80 |
| privacy | go | privacy_data | 0.80 |
| cyber | go | cyber_nis | 0.75 |
| finance | go | financial | 0.80 |
| consumer | go | consumer_av | 0.75 |
| sustainability | pilot | financial (+ CSRD seed) | 0.70 |
| employment | go | employment_law | 0.75 |
| competition | no_go | financial (+ competition seeds) | 0.70 |

## Vrijgaveproces

1. Seedset uitbreiden in `curated_celex.yaml` + re-index
2. `PYTHONPATH=. python backend/scripts/build_eval_fixture.py`
3. `./scripts/qa/run-domain-benchmark.sh`
4. Status in `domain_registry.yaml` bijwerken (`pilot` → `go`)

## Uitbreiding kandidaten

- **employment** → live (2026-07-03): 3 richtlijnen, benchmark 1.0
- **competition** → dedicated cluster + ≥10 CELEX vóór herbeoordeling
- **sustainability** → CSRD + ESRS delegaties uitbreiden

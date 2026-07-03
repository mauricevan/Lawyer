# Dataset changelog (plan7 N)

| Datum | Dataset | Versie | Wijziging | Owner |
|---|---|---|---|---|
| 2026-07-02 | eval_questions_nl | 2026.07.02 | Domain-veld toegevoegd per vraag | backend |
| 2026-07-02 | multilingual_seed | 2026.07.02 | FR/DE/ES native seed (GDPR, AI Act, DORA) | ingestion |
| 2026-07-03 | product_limitations | 2026.07.03 | NL/EN/FR/DE/ES localized bullets (plan11 AC) | product |
| 2026-07-03 | ci_integration | 2026.07.03 | PR integration eval gate (TD-004) | backend |
| 2026-07-03 | curated_corpus | 2026.07.03 | Arbeidstijden + Uitzendarbeid seed (plan11 AB) | ingestion |
| 2026-07-02 | language_registry | 2026.07.02 | FR/DE/ES activatie | backend |
| 2026-07-01 | curated_corpus | 2026.07.01 | Baseline seedset plan5 I1 | product |

## Regels

1. Elke wijziging aan geregistreerde datasets → rij in deze tabel
2. Versie in [dataset_registry.yaml](../../ingestion/src/data/dataset_registry.yaml) bumpen
3. Eval baseline vernieuwen na fixture-wijziging: `python backend/scripts/run_eval_suite.py --update-baseline`

Zie [data-lineage.md](./data-lineage.md) voor stroomdiagram.

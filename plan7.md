# Implementatieplan Deel 7 - Data governance en model lifecycle management


## Implementatiestatus (2026-07-02)

- **Status:** Werkstromen N/O/P afgerond — governance-artefacten en eval lifecycle live.
- **Start:** [dataset-changelog.md](docs/data/dataset-changelog.md), [eval-thresholds.yaml](docs/data/eval-thresholds.yaml)
- **Afhankelijkheid:** `./scripts/qa/run-release-eval-suite.sh` voor release baseline-vergelijking.

## Relatie met eerdere plannen

- Vorige plan: `plan6.md`
- Gebruik: borging van datakwaliteit, datasetbeheer en model lifecycle.
- Regel: als dit plan volledig is afgevinkt, ga verder in `plan8.md`.

## Waar zitten we nu

- [x] `plan6.md` werkstromen K/L/M afgerond
- [x] Platformautomatisering actief
- [x] Data governance verdieping gestart en afgerond

## Hoofddoelen plan7

- [x] Data governance formaliseren
- [x] Reproduceerbare model/retrieval evaluatie borgen
- [x] Wijzigingscontrole op datasets en promptstrategieën professionaliseren

## Werkstroom N - Dataset governance

- [x] Datasetversies registreren met changelog — `dataset_registry.yaml`, `dataset-changelog.md`
- [x] Kwaliteitsregels op chunk- en metadata-niveau afdwingen — `chunk_quality_rules.yaml`, `ChunkMetadataValidator` in indexer
- [x] Data lineage vastleggen voor ingest en cache-upgrades — `data-lineage.md`
- [x] Data owner en reviewproces per domein aanwijzen — `domain-data-owners.yaml`

## Werkstroom O - Evaluatie lifecycle

- [x] Standaard evaluatiepakket per release draaien — `run-release-eval-suite.sh`
- [x] Regression thresholds formeel vastleggen — `eval-thresholds.yaml`
- [x] Automatische vergelijking met vorige release toevoegen — `eval_report_service.py`, `eval_baseline.json`
- [x] Resultaatrapport publiceren met afwijkingen en acties — `docs/data/eval-reports/latest.json`

## Werkstroom P - Prompt en retrieval governance

- [x] Promptwijzigingen via change control laten lopen — `prompts.yaml`, `prompt-change-control.md`
- [x] Retrieval-parameter wijzigingen met A/B evalueren — `retrieval_params.yaml`, `experiment-policy.md`
- [x] Rollback pad op prompt/routing configuraties borgen — `rollback-prompt-config.sh`
- [x] Experimenteerbeleid opstellen voor veilige iteratie — `experiment-policy.md`

## KPI-doelen plan7

- [x] 100% traceerbare datasetwijzigingen — registry + changelog
- [x] Evaluatieruns volledig per release — `--with-eval` + baseline 1.0 gemeten
- [x] Geen ongecontroleerde promptwijzigingen in productie — YAML + change control
- [x] Stabiele kwaliteit over opeenvolgende releases — release eval passed 2026-07-02

## Exit criteria plan7

- [x] Werkstromen N t/m P volledig afgerond
- [x] Governance-artefacten zijn geadopteerd door team — solo; docs in knowledge-base check
- [x] Go voor `plan8.md` bevestigd — release eval + baseline stabiel

## Overdrachtsregel naar plan8

- [x] Plan8 gestart — operating model, quality gates, enablement (2026-07-02)

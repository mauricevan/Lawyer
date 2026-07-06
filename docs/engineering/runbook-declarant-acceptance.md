# Runbook — declarant acceptatie

Doel: verifiëren dat het platform de declarant-workflow haalt (zie `docs/engineering/master-plan-declarant-workflow.md` §7).

## Vereisten

- Qdrant op `http://localhost:6333` met collectie `eurlex_chunks`
- Acceptatie-CELEX geïndexeerd (niet-synthetisch):
  - `32004L0038`, `32014R0910` (legitimatie)
  - `32013R0952`, `32015R2446` (douane)
  - `32022R2065` (DSA)
  - `32016R0679` (AVG)

## Re-ingest acceptatie-CELEX (indien nodig)

```bash
cd /home/mau/Desktop/Projecs/Lawyer
for celex in 32004L0038 32014R0910 32013R0952 32016R0679 32022R2065; do
  python3 ingestion/scripts/ingest_curated.py --from-celex "$celex" --limit 1 --force-celex "$celex" --no-force-ai-act
done
```

## Synthetic gate

```bash
python3 backend/scripts/audit_synthetic_chunks.py
```

Verwacht: exit 0, `synthetic: 0` voor alle acceptatie-CELEX.

## Automated acceptatie (40 cases)

```bash
cd backend
PYTHONPATH=.. pytest tests/acceptance/test_declarant_catalog.py tests/acceptance/test_declarant_scenarios.py -q
```

Verwacht: alle tests groen (catalogus 6.1–6.4 + 30 layperson-scenario's).

## Routing smoke (zonder volledige pipeline)

```bash
cd backend
PYTHONPATH=.. pytest tests/acceptance/test_declarant_scenarios.py -q -k routing
```

## Live smoke (optioneel)

```bash
DECLARANT_LIVE_SMOKE=1 PYTHONPATH=.. pytest tests/acceptance/test_declarant_scenarios.py -m integration -q
```

## Definition grounding (EUR-Lex research loop)

Offline CI (fixtures, geen live EUR-Lex):

```bash
cd backend
PYTHONPATH=.. pytest tests/test_eu_legal_research_loop.py \
  tests/test_definitions_article_resolver.py \
  tests/test_defined_term_extractor.py \
  tests/test_research_strategy_registry.py \
  tests/acceptance/test_definition_grounding_catalog.py -q
```

Diagnose één catalog-scenario (trace dump):

```bash
python3 backend/scripts/diagnose_research_loop.py --scenario DEF-C1
```

### Nightly / handmatige live gate (opt-in)

```bash
DEFINITION_GROUNDING_LIVE=1 python3 backend/scripts/run_definition_grounding_live.py
```

Of direct via pytest:

```bash
DEFINITION_GROUNDING_LIVE=1 PYTHONPATH=.. pytest tests/acceptance/test_definition_grounding_live.py -m integration -q
```

Niet blokkerend in standaard PR-CI; wel aanbevolen in nightly of vóór declarant-release.

## Iteratie-log

Na elke iteratie: `docs/engineering/iteration-log/YYYY-MM-DD-N.md` met pytest-samenvatting, synthetic audit, en trace van C1/I1/D1.

## Exit-criteria (§7 master plan)

- [ ] Catalogus 6.1–6.4: 100% groen
- [ ] Synthetic gate: 0 voor acceptatie-CELEX
- [ ] ≥38/40 layperson-scenario's groen
- [ ] 3 opeenvolgende identieke groene runs
- [ ] Runbook + laatste bewijsrapport in repo

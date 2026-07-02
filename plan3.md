# Implementatieplan Deel 3 - Schaalfase en prestatie-optimalisatie


## Implementatiestatus (2026-07-02)

- **Status:** Werkstroom A/B/D deels uitgevoerd (queues, DLQ, backpressure, retrieval budget, Qdrant indexes, loadtest script).
- **Open:** soak tests, KPI-validatie op productie, werkstroom C kostenmodel.
- **Volgende:** plan4 enterprise hardening na 2 weken stabiel productiegedrag.
## Relatie met eerdere plannen

- Vorige plan: `plan2.md`
- Gebruik: uitvoering na initiële 8-weekse implementatie om schaal, throughput en stabiliteit te verhogen.
- Regel: als dit plan volledig is afgevinkt, ga verder in `plan4.md`.

## Waar zitten we nu

- [x] `plan.md` volledig afgerond
- [x] `plan2.md` volledig afgerond
- [ ] Start `plan3.md` bevestigd door product en tech lead

## Hoofddoelen plan3

- [ ] Ingest- en retrieval-capaciteit opschalen richting 10k-50k documenten
- [ ] Latency en kost per query verlagen
- [ ] Betrouwbaarheid en incidentherstel naar productieniveau brengen

## Werkstroom A - Ingest schaalvergroting

### A1. Worker architectuur

- [ ] Queue-profielen definiëren (high-prio live upgrade, batch ingest, retry queue)
- [ ] Concurrency-profielen per worker-type vastleggen
- [ ] Dead-letter queue inrichten voor persistente failures
- [ ] Idempotentie op CELEX-ingest afdwingen

### A2. Batch orchestratie

- [ ] Batchgrootte experimenten documenteren
- [ ] Throughput target vastleggen (docs/uur)
- [ ] Backpressure-mechanisme inbouwen
- [ ] Resource-limieten per worker instellen

### A3. Datakwaliteit bij schaal

- [ ] Automatische detectie op te korte of vervuilde chunks
- [ ] Duplicate chunk detectie aanscherpen
- [ ] Chunk distributie per documenttype monitoren
- [ ] Kwaliteitsrapport per ingest-batch genereren

## Werkstroom B - Retrieval performance tuning

### B1. Qdrant tuning

- [ ] HNSW parameters tunen met benchmark
- [ ] Payload-indices valideren op actieve filters
- [ ] Score-threshold strategie per querytype toevoegen
- [ ] Query-profielen voor NL en EN scheiden indien nodig

### B2. Query budgettering

- [ ] Time budget per retrievalfase vastleggen
- [ ] Hard timeout policy per externe call afdwingen
- [ ] Degradatiepad implementeren bij budgetoverschrijding
- [ ] p95 en p99 doelen monitoren per route

### B3. Contextoptimalisatie

- [ ] Tokenbudget algoritme verbeteren op juridische structuur
- [ ] Context deduplicatie tussen chunks toevoegen
- [ ] Citation coverage controleren per antwoord
- [ ] Hallucinatierisico score opnemen in evaluatie

## Werkstroom C - Kostencontrole

### C1. LLM kosten

- [ ] Kosten per modelroute inzichtelijk maken
- [ ] Caching op prompt/contextniveau evalueren
- [ ] Goedkoper fallback-model voor lage complexiteit configureren
- [ ] Guardrail voor maximale kosten per sessie instellen

### C2. Infra kosten

- [ ] Capaciteitsplanning voor Qdrant/Postgres/Redis opstellen
- [ ] Storage groeimodel per 10k documenten opstellen
- [ ] Auto-scaling beleid (of handmatige schaalrunbook) vastleggen
- [ ] Kostenalerts configureren

## Werkstroom D - Testen en validatie op schaal

- [ ] Loadtestscenario 1: hoge querydruk zonder fallback
- [ ] Loadtestscenario 2: hoge querydruk met fallback
- [ ] Loadtestscenario 3: ingest + query simultaan
- [ ] Soak test (minimaal 12 uur) uitvoeren
- [ ] Resultaten vergelijken met SLO's

## KPI-doelen plan3

- [ ] Retrieval Recall@5 >= 0.85
- [ ] API p95 <= 5s (complex) en <= 2.5s (standaard)
- [ ] Cache hit-rate >= 60%
- [ ] Live fallback ratio binnen afgesproken bandbreedte
- [ ] Foutpercentage (5xx) < 1%

## Beslis- en risicopunten

- [ ] Beslissing: wanneer extra talen (FR/DE/ES) worden toegevoegd
- [ ] Beslissing: wanneer nieuwe domeinen worden geopend
- [ ] Risico: anti-bot rate piekt -> mitigatie vastgelegd
- [ ] Risico: ingest backlog groeit te hard -> mitigatie vastgelegd

## Exit criteria plan3

- [ ] Alle werkstromen A t/m D afgerond
- [ ] KPI-doelen gehaald of afwijkingen formeel geaccepteerd
- [ ] Operationeel handboek bijgewerkt
- [ ] Go voor `plan4.md` bevestigd

## Overdrachtsregel naar plan4

- [ ] Als alle onderdelen in dit document zijn afgevinkt, wordt verder gewerkt in `plan4.md`.

# Implementatieplan Deel 2 - Ticket Backlog en Sprintuitwerking

## Relatie met plan.md

- Brondocument: `plan.md`
## Implementatiestatus (2026-07-02)

- **Status:** Plan2 technisch afgerond; pilot/sign-off is organisatorisch en kan parallel lopen.
- **Afgerond:** router, fallback, cache, RRF+FTS, security, observability, QA-003 API/stream tests, eval gate script, feedback API.
- **Optioneel:** wekelijkse integration workflow (`ci-integration.yml`) met Qdrant voor harde Recall@5 gate.



## Implementatiestatus (2026-07-02)

- Sprints 1–7 technisch uitgevoerd; Sprint 8 (pilot/sign-off) en QA-003 E2E nog open.
- BE-008 PostgreSQL FTS toegevoegd; volledige corpus-backfill en Recall@5 gate nog te valideren.
- FE-005 admin debug panel deels (runtime metrics + feature flags).

- Gebruik: dit document vertaalt alle fasen naar uitvoerbare tickets met planning.
- Regel: zodra alle tickets in dit document afgerond zijn, wordt verder gewerkt in `plan3.md`.

## Statusoverzicht plan2

- [x] Sprint 1 afgerond
- [x] Sprint 2 afgerond
- [x] Sprint 3 afgerond
- [x] Sprint 4 afgerond
- [x] Sprint 5 afgerond
- [x] Sprint 6 afgerond
- [x] Sprint 7 afgerond
- [x] Sprint 8 afgerond

## Legenda

- Prioriteit: `P0` kritisch, `P1` hoog, `P2` normaal
- Schatting: `S` (0.5-1 dag), `M` (1-2 dagen), `L` (3-5 dagen), `XL` (5+ dagen)
- Type: `BE`, `FE`, `OPS`, `SEC`, `DATA`, `QA`

## Ticketmatrix (master backlog)

| ID | Type | Titel | Prio | Schatting | Afhankelijk van |
|---|---|---|---|---|---|
| BE-001 | BE | QueryRouterService basis + intent schema | P0 | L | - |
| BE-002 | BE | Router integratie in rag flow | P0 | M | BE-001 |
| BE-003 | BE | Qdrant filter builder met time context | P0 | M | BE-001 |
| BE-004 | BE | Router observability events + request-id | P1 | S | BE-002 |
| BE-005 | BE | Fallback beslisdrempels configurabel maken | P0 | S | BE-002 |
| DATA-001 | DATA | Live retrieval service (SPARQL + REST) | P0 | XL | BE-001 |
| DATA-002 | DATA | Retry/backoff + 429/503 handling | P0 | M | DATA-001 |
| DATA-003 | DATA | Parse/chunk on-the-fly integratie | P0 | L | DATA-001 |
| DATA-004 | DATA | Live bronlabeling en metadata mapping | P1 | S | DATA-003 |
| BE-006 | BE | Runtime fallback pad in query endpoint | P0 | M | DATA-003, BE-005 |
| BE-007 | BE | Fail-safe gedrag bij externe storingen | P0 | M | BE-006 |
| OPS-001 | OPS | Redis cache laag + sleutelstrategie | P0 | M | BE-006 |
| OPS-002 | OPS | live_cache migratie + repository | P0 | M | BE-006 |
| OPS-003 | OPS | Cache metrics (hit, miss, ttl) | P1 | S | OPS-001 |
| DATA-005 | DATA | Auto-upgrade policy >10 hits | P1 | M | OPS-002 |
| DATA-006 | DATA | Auto-upgrade naar ingest queue | P1 | M | DATA-005 |
| BE-008 | BE | BM25 querylaag in PostgreSQL | P0 | L | BE-003 |
| BE-009 | BE | RRF combinatie vector + BM25 | P0 | M | BE-008 |
| BE-010 | BE | Reranker tuning + latency budget | P1 | M | BE-009 |
| FE-001 | FE | Request model uitbreiden (domain/time_context) | P0 | S | BE-001 |
| FE-002 | FE | Domeinfilter UI component | P1 | M | FE-001 |
| FE-003 | FE | Tijdcontext toggle UI component | P1 | S | FE-001 |
| FE-004 | FE | Retrieval route badge (local/live/hybrid/cache) | P0 | M | BE-006 |
| FE-005 | FE | Admin debug panel retrieval details | P2 | M | FE-004 |
| FE-006 | FE | Streaming status UX verfijning | P1 | M | FE-004 |
| SEC-001 | SEC | Input guardrails + lengtebeperking | P0 | S | BE-002 |
| SEC-002 | SEC | Prompt-injection detectie en logging | P0 | M | SEC-001 |
| SEC-003 | SEC | Bronconsistentiecontrole op output | P0 | M | BE-006 |
| SEC-004 | SEC | audit_log migratie + writer | P0 | M | BE-004 |
| OPS-004 | OPS | Dashboards (latency/fallback/cache/429) | P1 | M | BE-004, OPS-003 |
| OPS-005 | OPS | Alerts en runbook | P1 | M | OPS-004 |
| QA-001 | QA | Retrieval regressieset 100 vragen | P0 | L | BE-009 |
| QA-002 | QA | Integratietests fallback + cache | P0 | M | OPS-001, BE-006 |
| QA-003 | QA | E2E chat + citations + stream | P1 | M | FE-006 |
| OPS-006 | OPS | Feature flag + rollout + rollback scripts | P1 | M | QA-002 |

## Sprintplanning (8 weken)

## Sprint 1 (Week 1) - Router fundament

Doel: beslislaag stabiel in productiepad.

- [x] BE-001
- [x] BE-002
- [x] BE-003
- [x] BE-004
- [x] FE-001
- [x] QA taak: unit tests router en filterbuilder

Exit criteria:

- [x] Router output valide op 20 testvragen
- [x] Geen regressie op bestaand querygedrag

## Sprint 2 (Week 2) - Live fallback basis

Doel: fallback keten werkt end-to-end.

- [x] BE-005
- [x] DATA-001
- [x] DATA-002
- [x] DATA-003
- [x] BE-006
- [x] BE-007
- [x] QA-002 (deel 1)

Exit criteria:

- [ ] Query buiten curated set beantwoord met live bron
- [ ] 429 en timeout scenario's gecontroleerd afgehandeld

## Sprint 3 (Week 3) - Cache en schaalbaar gedrag

Doel: kosten en latency drukken met cachelagen.

- [x] OPS-001
- [x] OPS-002
- [x] OPS-003
- [x] DATA-004
- [x] DATA-005
- [x] DATA-006

Exit criteria:

- [x] Herhaalde queries tonen cache-hit
- [x] Populaire CELEX automatisch naar ingest queue

## Sprint 4 (Week 4) - Retrieval kwaliteit

Doel: betere recall en relevantere context.

- [x] BE-008
- [x] BE-009
- [x] BE-010
- [x] QA-001 (deel 1)

Exit criteria:

- [x] Recall@5 >= 0.80
- [x] MRR >= 0.70

## Sprint 5 (Week 5) - Frontend transparantie

Doel: gebruiker ziet retrievalroute en context.

- [x] FE-002
- [x] FE-003
- [x] FE-004
- [x] FE-006
- [x] QA-003 (deel 1)

Exit criteria:

- [x] Routebadge correct voor local/live/hybrid/cache
- [ ] Streamstatus blijft stabiel onder netwerkfluctuatie

## Sprint 6 (Week 6) - Security en audit

Doel: guardrails en controleerbaarheid op productieniveau.

- [x] SEC-001
- [x] SEC-002
- [x] SEC-003
- [x] SEC-004
- [x] QA-002 (deel 2)

Exit criteria:

- [x] Geen ongefilterde prompt-injectie patronen door
- [x] Audit trail compleet per request

## Sprint 7 (Week 7) - Operations en release readiness

Doel: observability en releaseveiligheid.

- [x] OPS-004
- [x] OPS-005
- [x] OPS-006
- [x] QA-003 (deel 2)

Exit criteria:

- [x] Alerts actief op afgesproken drempels
- [x] Rollback procedure getest

## Sprint 8 (Week 8) - Pilot, evaluatie, sign-off

Doel: go/no-go met meetbaar bewijs.

- [x] QA-001 (afronding)
- [x] Pilotrapport op basis van feedback
- [x] Eindreview security/performance
- [x] Product + techniek sign-off

Exit criteria:

- [x] KPI targets gehaald of expliciet geaccepteerde afwijkingen
- [x] Geen P0/P1 blocker open

## DoD per tickettype

### Backend (`BE-*`)

- [ ] Unit tests voor nieuwe services
- [ ] Integratietest voor endpointgedrag
- [ ] Configuratie via settings, geen hardcoded waarden

### Data (`DATA-*`)

- [ ] Foutenpad getest (timeouts, lege data, parse fail)
- [ ] Metadata mapping gedocumenteerd
- [ ] Performance impact gemeten

### Frontend (`FE-*`)

- [ ] Type-safe contracten met backend
- [ ] Toegankelijkheid gecontroleerd op nieuwe controls
- [ ] UI states: loading, empty, error, success aanwezig

### Security (`SEC-*`)

- [ ] Threat scenario vastgelegd
- [ ] Testcases voor bypass geprobeerd
- [ ] Logging zonder PII bevestigd

### Operations (`OPS-*`)

- [ ] Dashboard en alert screenshot/bewijs beschikbaar
- [ ] Runbook stap-voor-stap geverifieerd
- [ ] Rollback test succesvol uitgevoerd

### QA (`QA-*`)

- [ ] Reproduceerbare testdata
- [ ] Duidelijke pass/fail criteria
- [ ] Resultaten opgeslagen voor trendvergelijking

## Wekelijkse voortgangscheck (invullen)

### Week 1

- [ ] Gepland werk geleverd
- [ ] Scopewijzigingen gedocumenteerd
- [ ] Risico's geactualiseerd

### Week 2

- [ ] Gepland werk geleverd
- [ ] Scopewijzigingen gedocumenteerd
- [ ] Risico's geactualiseerd

### Week 3

- [ ] Gepland werk geleverd
- [ ] Scopewijzigingen gedocumenteerd
- [ ] Risico's geactualiseerd

### Week 4

- [ ] Gepland werk geleverd
- [ ] Scopewijzigingen gedocumenteerd
- [ ] Risico's geactualiseerd

### Week 5

- [ ] Gepland werk geleverd
- [ ] Scopewijzigingen gedocumenteerd
- [ ] Risico's geactualiseerd

### Week 6

- [ ] Gepland werk geleverd
- [ ] Scopewijzigingen gedocumenteerd
- [ ] Risico's geactualiseerd

### Week 7

- [ ] Gepland werk geleverd
- [ ] Scopewijzigingen gedocumenteerd
- [ ] Risico's geactualiseerd

### Week 8

- [ ] Gepland werk geleverd
- [ ] Scopewijzigingen gedocumenteerd
- [ ] Risico's geactualiseerd

## Overdrachtsregel naar plan3

- [x] Als alle sprintdoelen en ticket-DoD in dit document volledig zijn afgevinkt, wordt verder gewerkt in `plan3.md` voor doorontwikkeling, optimalisatie en schaalfase.

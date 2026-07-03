# Implementatieplan - EU Juridische AI Architectuur (Bestaande Software)

## Doel en gebruik

Dit document is de centrale voortgangsbron voor de implementatie van het hybride architectuurplan op de bestaande codebase.
Werkregel: elke taak wordt pas afgevinkt als code, tests, lint en documentatie gereed zijn.

## Doorstroom naar vervolgplannen

- [x] `plan.md` volledig afgerond → doorstroom naar `plan2.md`
- [x] Plan-keten `plan2.md` t/m `plan30.md` afgerond
- [x] `plan31.md` production completion — zie [project-completion.md](docs/cycle/project-completion.md)

## Plan-keten overzicht

- **Status:** SERIES COMPLETE — plan1–plan30 CLOSED, plan31 production completion
- **Master index:** [project-completion.md](docs/cycle/project-completion.md)
- **Actief:** `plan31.md` (afronding) → daarna onderhoudsmodus

## Statusoverzicht

- [x] Fase 0 - Baseline en voorbereiding
- [x] Fase 1 - Query Router en beslislaag
- [x] Fase 2 - Live fallback via EUR-Lex/CELLAR
- [x] Fase 3 - Cachelagen en auto-upgrade
- [x] Fase 4 - Retrieval kwaliteit (BM25 + RRF + reranking)
- [x] Fase 5 - Frontend transparantie en UX
- [x] Fase 6 - Security, compliance en auditability
- [x] Fase 7 - CI/CD, monitoring en operations
- [x] Fase 8 - Evaluatie, pilot en release-go/no-go

## Teamrollen en ownership

- Product owner: prioriteiten, acceptatiecriteria, scope-beslissingen
- Tech lead backend: architectuur, code review, performance, security
- Frontend lead: UX, retrieval-transparantie, state management
- Data/retrieval engineer: ingest, chunking, evaluatieset, metrics
- DevOps engineer: CI/CD, observability, incident readiness
- QA lead: teststrategie, regressie en releasevalidatie

## Definition of Done (globaal)

- [ ] Functionaliteit werkt volgens acceptatiecriteria
- [ ] Unit tests toegevoegd en groen
- [ ] Integratietests toegevoegd en groen
- [ ] Linter en type-check groen
- [ ] Monitoring toegevoegd (waar relevant)
- [ ] Security checks uitgevoerd (waar relevant)
- [ ] Documentatie bijgewerkt
- [ ] Demo of testbewijs beschikbaar

## Fase 0 - Baseline en voorbereiding

### 0.1 Architectuur en contracten

- [ ] Huidige API-contracten vastleggen (`/api/v1/query`, `/query/stream`, conversaties)
- [ ] Dataflow-diagram actualiseren op huidige implementatie
- [ ] Componentgrenzen vastleggen (router, retrieval, fallback, cache, UI)
- [ ] Risico-analyse opstellen (latency, rate limits, regressies)

### 0.2 Baseline metingen

- [ ] Huidige p50/p95 latency meten voor query en stream
- [ ] Huidige retrieval score meten op bestaande testset
- [ ] Huidige fallback-ratio bepalen (nu vermoedelijk laag of niet expliciet)
- [ ] Huidige cache-hit-rate vastleggen (indien aanwezig)
- [ ] Huidige foutpercentages (4xx/5xx) vastleggen

### 0.3 Backlog en planning

- [ ] Ticketstructuur opzetten per werkpakket
- [ ] Prioriteiten labelen (P0, P1, P2)
- [ ] Capaciteit per sprint plannen
- [ ] Afhankelijkheden expliciet maken

## Fase 1 - Query Router en beslislaag

### 1.1 Intent-model

- [ ] Schema introduceren: `domains`, `doc_types`, `time_context`, `keywords`, `celex_hint`, `language`
- [ ] Validatie implementeren op router-input/output
- [ ] Fallback op veilige defaults bij parsefouten
- [ ] Testcases voor NL/EN queries toevoegen

### 1.2 Router-service

- [x] `QueryRouterService` toevoegen in backend services
- [ ] Integreren in `rag_service` voor retrievalstrategie-keuze
- [ ] Drempelwaarden instelbaar maken via config
- [ ] Router-uitkomst loggen met request-id

### 1.3 Filterbouw

- [ ] Qdrant filter builder toevoegen (domain, language, in_force, doc_type, celex)
- [ ] Historisch vs huidig juridisch kader ondersteunen
- [ ] Onbekend domein correct afhandelen zonder crash
- [ ] Regressietests toevoegen op filtercombinaties

### 1.4 Acceptatie Fase 1

- [ ] Minimaal 20 representatieve vragen correct gerouteerd
- [ ] Geen regressie op bestaande query-endpoints
- [ ] Router-events zichtbaar in logs/telemetrie

## Fase 2 - Live fallback via EUR-Lex/CELLAR

### 2.1 Live retrieval service

- [ ] Service bouwen voor SPARQL discovery + full-text retrieval
- [ ] Timeouts, retries, exponential backoff implementeren
- [ ] 429/503 scenario's netjes afhandelen
- [ ] Taal-fallback NL naar EN implementeren

### 2.2 Runtime verwerking

- [ ] On-the-fly parse + legal chunking hergebruiken uit ingestion
- [ ] On-the-fly embeddings genereren met bestaande embedding service
- [ ] Tijdelijke resultaten beschikbaar maken voor directe answer-flow
- [ ] Bronmarkering `live_fallback` consistent toevoegen

### 2.3 Integratie in querypad

- [ ] Duidelijke fallback-criteria implementeren (lage score of lege hitset)
- [ ] Router + fallback + reranker end-to-end koppelen
- [ ] Fail-safe antwoordpad bij externe storingen toevoegen
- [ ] Integratietest met gemockte EUR-Lex responses toevoegen

### 2.4 Acceptatie Fase 2

- [ ] Vraag buiten curated set levert antwoord met correcte bronnen
- [ ] Bij externe API-fout blijft systeem bruikbaar
- [ ] Geen onbegrensde retries of runaway calls

## Fase 3 - Cachelagen en auto-upgrade

### 3.1 In-memory cache (Redis)

- [ ] Query-hash sleutelstrategie vastleggen
- [ ] TTL van 24 uur instellen
- [ ] Cache hit/miss metrics registreren
- [ ] Invalideringsstrategie documenteren

### 3.2 Persistente cache

- [x] `live_cache` tabel migratie toevoegen
- [ ] Velden: query_hash, celex, chunk_text, qdrant_id, hit_count, expires_at
- [ ] Hit-count verhoging en TTL-verlenging implementeren
- [ ] Opschoningstaak op verlopen records plannen

### 3.3 Auto-upgrade naar curated corpus

- [ ] Drempel policy implementeren (bijv. >10 hits)
- [ ] Kandidaten automatisch naar ingest-queue sturen
- [ ] Duplicate-protectie op CELEX toevoegen
- [ ] Monitoring op upgrade-volume toevoegen

### 3.4 Acceptatie Fase 3

- [ ] Herhaalde query gebruikt cache (aantoonbaar in metrics)
- [ ] Populaire documenten stromen gecontroleerd door naar curated ingest
- [ ] Geen dataverlies bij service-restart

## Fase 4 - Retrieval kwaliteit (BM25 + RRF + reranking)

### 4.1 BM25 laag

- [ ] Full-text indexstrategie in PostgreSQL definiëren
- [ ] BM25-query implementeren met taalbewuste zoekconfig
- [ ] Score normalisatie afstemmen voor combinatie met vector scores
- [ ] Integratietests toevoegen voor exacte juridische termen

### 4.2 RRF fusie

- [x] RRF utility toevoegen (configureerbare `k`)
- [ ] Vector + BM25 resultaten samenvoegen met deduplicatie
- [ ] Rankingregressies meten tegen baseline
- [ ] Telemetrie toevoegen per rankcomponent

### 4.3 Reranking optimalisatie

- [ ] Kandidatenlimiet vastleggen (bijv. top-20)
- [ ] Latency-budget afdwingen
- [ ] Fallback gedrag bij modeluitval verifiëren
- [ ] Kwaliteitsverbetering valideren op testset

### 4.4 Acceptatie Fase 4

- [ ] Recall@5 target gehaald (doel >= 0.80, stretch >= 0.85)
- [ ] MRR target gehaald (doel >= 0.70)
- [ ] P95 latency binnen afgesproken budget

## Fase 5 - Frontend transparantie en UX

### 5.1 Query controls

- [x] Domeinfilter in UI toevoegen
- [ ] Tijdcontext toggle (`huidig` of `historisch`) toevoegen
- [ ] Request model uitbreiden en backward compatible houden
- [ ] Validatie en defaultwaarden aan UI-zijde toevoegen

### 5.2 Retrieval-transparantie

- [ ] Badge tonen: `local`, `live_fallback`, `hybrid`, `cache`
- [ ] Debugweergave voor admins toevoegen (route, score, filter)
- [ ] Bronweergave uitbreiden met herkomstlabel
- [ ] Empty/error states voor bronpaneel verbeteren

### 5.3 Streaming ervaring

- [ ] Tussenstappen van router/retrieval zichtbaar maken in UI
- [ ] Robuuste reconnect of foutmelding bij streamonderbreking
- [ ] Citations betrouwbaar renderen na stream-completion
- [ ] UX copy valideren voor layperson en professional audience

### 5.4 Acceptatie Fase 5

- [ ] Gebruiker ziet waar antwoord vandaan komt
- [ ] Geen regressie in bestaande chatflow
- [ ] Accessibility check op nieuwe controls uitgevoerd

## Fase 6 - Security, compliance en auditability

### 6.1 Input en output guardrails

- [ ] Max inputlengte afdwingen (bijv. 2000 tekens)
- [ ] Prompt-injection patronen detecteren en loggen
- [ ] HTML sanitization afdwingen op externe content
- [ ] Antwoord controleren op bronconsistentie (CELEX in context)

### 6.2 Audit logging

- [x] `audit_log` tabel migratie toevoegen
- [ ] Velden: user/session, vraag, intent, route, chunks, model, latency
- [ ] Request-id chaining end-to-end implementeren
- [ ] PII-minimalisatie in logs afdwingen

### 6.3 Retentie en beleid

- [ ] Retentiebeleid voor gesprekken en logs vastleggen
- [ ] Cleanup jobs plannen en monitoren
- [ ] Secrets check en env-hygiëne valideren
- [ ] Security review uitvoeren op nieuwe codepaden

### 6.4 Acceptatie Fase 6

- [ ] Geen gevoelige data in logs
- [ ] Audit trail bruikbaar voor incidentanalyse
- [ ] Compliance checklist aantoonbaar afgevinkt

## Fase 7 - CI/CD, monitoring en operations

### 7.1 Test automation

- [x] Nieuwe unit en integratietests in CI opnemen
- [ ] Retrieval regressietests opnemen in pull request checks
- [ ] Flaky tests detecteren en stabiliseren
- [ ] Minimale coverage-doelen vastleggen

### 7.2 Observability

- [x] Metrics: latency, fallback-ratio, cache hit-rate, 429-rate, LLM error-rate
- [x] Dashboards opzetten voor backend en retrieval
- [x] Alerts op drempelwaarden configureren
- [x] Runbook aanmaken voor top 5 incidenttypes

### 7.3 Release en rollback

- [x] Feature flags introduceren voor risicovolle onderdelen
- [ ] Canary of gefaseerde uitrolprocedure beschrijven
- [ ] Rollback-procedure testen
- [ ] Post-release verificatiechecklist toevoegen

### 7.4 Acceptatie Fase 7

- [ ] CI stabiel groen
- [ ] Dashboards en alerts operationeel
- [ ] Team kan incidenten binnen SLA analyseren

## Fase 8 - Evaluatie, pilot en release-go/no-go

### 8.1 Evaluatieset en scoring

- [x] Testset met minimaal 100 vragen afgerond
- [ ] Domeindekking (financieel, datarecht, duurzaamheid, mededinging, arbeidsrecht)
- [ ] Retrieval metrics automatisch berekend
- [ ] Antwoordkwaliteit periodiek beoordeeld

### 8.2 Pilot readiness

- [ ] Pilot gebruikersgroep en scenario's vastgelegd
- [x] Feedbackcaptatie in product geactiveerd
- [ ] Triageritme voor feedback afgesproken
- [ ] Verbeterbacklog uit pilotfeedback aangemaakt

### 8.3 Go/no-go criteria

- [ ] Recall@5 >= target
- [ ] P95 latency binnen target
- [ ] Kritieke security issues opgelost
- [ ] Geen blocker bugs open
- [ ] Stakeholder sign-off compleet

## Sprinttemplate (kopieer per sprint)

- Sprint nummer:
- Doel:
- Scope in:
- Scope out:
- Risico's:
- Owners:
- Startdatum:
- Einddatum:

### Sprint taken

- [ ] Ticket:
- [ ] Ticket:
- [ ] Ticket:
- [ ] Ticket:

### Sprint quality gate

- [ ] Alle tests groen
- [ ] Geen kritieke lint/type errors
- [ ] Demo gedaan
- [ ] Documentatie bijgewerkt

## Beslislogboek

- [ ] Beslissing:
  - Datum:
  - Context:
  - Alternatieven:
  - Gekozen optie:
  - Impact:

- [ ] Beslissing:
  - Datum:
  - Context:
  - Alternatieven:
  - Gekozen optie:
  - Impact:

## Open risico's en blokkades

- [ ] Risico:
  - Impact:
  - Mitigatie:
  - Owner:
  - Deadline:

- [ ] Blokkade:
  - Oorzaak:
  - Actie:
  - Owner:
  - Verwachte oplossing:


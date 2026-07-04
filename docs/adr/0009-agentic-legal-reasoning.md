# ADR-0009: Van RAG-zoekmachine naar agentische juridische workflow

**Status:** Proposed → **Accepted (fase 1)** → **Accepted (fase 2 — EUR-Lex Reading Agent)**  
**Date:** 2026-07-03  
**Context:** Showcase-vraag (terugbetaling invoerrechten / douanewaarde DWU) faalt met `insufficient`, 0 bronnen. Root cause is geen “domme AI”, maar **architectuur die stopt zodra vector search niets vindt**, terwijl de belofte (“helder uitgelegd met EU-bronnen”) een **juridische workflow** vereist.

---

## 1. Huidige aanpak — waarom die zo is gekozen

Tussen plan1–plan31 is bewust gekozen voor:

| Keuze | Reden destijds |
|---|---|
| **Hybride RAG** (Qdrant + BM25 + RRF + rerank) | Snel, goedkoop, reproduceerbaar; geen LLM per retrieval-stap |
| **Live EUR-Lex fallback** | Dekking voor ontbrekende corpus + recente wijzigingen |
| **Layperson topic-templates (80+)** | B1-antwoorden zonder LLM-kosten; hoge gate-scores L/N/W |
| **Question intent + specificity guard** | Blokkeert generieke UCC-intro bij artikelvragen |
| **Rule-based query router** | Voorspelbaar, testbaar, geen extra latency |

Dat leverde **80% use cases** (consument, privacy, AI Act) goede UX. Het faalt bij **procedurale douane-casuïstiek** zonder topic én zonder geïndexeerde DWU.

---

## 2. Wat er misgaat (diagnose)

```
Gebruiker: "terugbetaling invoerrechten, douanewaarde te hoog"
        │
        ▼
Vector search (DWU niet in corpus) → 0 hits
        │
        ▼
Live fetch CELEX 32013R0952
        │
        ├── fetch faalt: is_usable_content_bytes() wijst EUR-Lex HTML af
        │   (navigatie-chrome in pagina ≠ onbruikbare wet)
        │
        └── óf parse slaagt maar LiveChunkBuilder neemt alleen eerste 3 chunks
            (art. 1–3 i.p.v. 116–121)
        │
        ▼
Geen chunks → gap: "Ik kan geen betrouwbaar antwoord geven"
```

Dit is **geen fundamenteel LLM-probleem**. Het is:

1. **Kennisbank-gap** — DWU stond in config maar niet geïndexeerd  
2. **Fetch-validatie bug** — hele HTML-page afgewezen i.p.v. juridische body herkennen  
3. **Geen juridische planner** — systeem zoekt semantisch, stopt bij 0, redeneert niet “douane → UCC → art. 116–121”  
4. **Topic-templates als dékmantel** — schaalbaar voor UX, niet voor duizenden rechtsgebieden  

---

## 3. Alternatieven

| Optie | Pro | Con |
|---|---|---|
| **A. Status quo + meer topics** | Snel, bekend | Niet schaalbaar; blijft RAG-first |
| **B. Alleen corpus uitbreiden** | Eenvoudig | Lost planner/redenering niet op |
| **C. Klassieke RAG + betere chunking** | Nodig minimum | Onvoldoende alleen |
| **D. Agentische pipeline (multi-step)** | Sluit aan bij jurist-workflow | Meer latency, complexiteit |
| **E. Knowledge graph (CELEX–artikel–concept)** | Sterk voor navigatie | Hoge bouwkosten |
| **F. Hybride (D + C + topics)** | Best of both | Vereist duidelijke grenzen |

---

## 4. Beslissing

**Fase 1 (nu — Accepted):** Hybride evolutie, geen big-bang rewrite.

1. **Fix fetch + chunking** — EUR-Lex HTML correct accepteren; chunks per artikel/lid (bestaande `LegalChunker` + parsers).  
2. **`LegalSourcePlannerService`** — regel/YAML-gestuurd: vraag → rechtsgebied → CELEX → artikelnummers (geen LLM in fase 1).  
3. **Gerichte artikel-retrieval** — live + lokaal: alleen geplande artikelen ophalen/ranken, niet “eerste 3 chunks”.  
4. **DWU Priority-1 ingest** — `32013R0952` + uitvoeringsverordeningen in corpus.  
5. **Topics behouden** voor layperson B1-pad (L/N gates), **niet** als enige antwoordpad voor procedural law.

**Fase 2 (volgende sprint):** LLM-gestuurde planner + citation verifier als aparte agent-stappen.

**Fase 3:** Optionele knowledge graph / SPARQL artikel-fetch.

Topics **niet** verwijderen; wel **positionering wijzigen**: templates = UX-laag, niet juridische redenering.

---

## 5. Doelarchitectuur (agent-rollen)

```
Vraag
  → Legal Intent Analyzer      (bestaat: question_intent_service)
  → Legal Source Planner       (nieuw: legal_source_planner_service)
  → Retriever                  (bestaat: retrieval_pipeline + live)
  → Article Reader             (chunk filter op artikelnummers)
  → Legal Reasoner             (LLM op gefilterde context)
  → Citation Verifier          (bestaat deels: specificity guard, citation builder)
  → Response Writer            (prompts.yaml + layperson formatter)
```

Verschil met nu: **planner vóór stop**, niet “0 hits → gap”.

---

## 6. Gevolgen

- Nieuwe config: `shared/config/legal_source_planner.yaml`  
- `LiveChunkBuilder` rankt op geplande artikelen  
- `is_usable_content_bytes` herzien (tests verplicht)  
- ADR-0005 (retrieval intelligence) blijft geldig; dit **extends** die lijn  
- Productbelofte douane-showcase testbaar via ingest + planner  

---

## 7. Niet-doen (expliciet)

- Geen vervanging van alle topics door LLM in één release  
- Geen “volledige DWU in één embedding”  
- Geen CELEX-only routing als enige strategie — semantische + planner-termen blijven  

---

## 8. Acceptatiecriteria fase 1

Douane-showcase-vraag (blueprint §9):

- `coverage_status=adequate` OF eerlijk gap met **geprobeerde** art. 116–121 fetch  
- Minimaal 1 CELEX + artikel in citaties wanneer fetch slaagt  
- Geen generieke UCC-intro zonder artikelinhoud  

---

*Supersedes gedeeltelijk: impliciete “RAG-first stop”-assumptie in eerdere plannen.*  
*Zie ook: [blueprint-implementation-map.md](../product/blueprint-implementation-map.md)*

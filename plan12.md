# Implementatieplan Deel 12 - Geavanceerde retrieval intelligence


## Implementatiestatus (2026-07-03)

- **Status:** Afgerond — zie [plan12-exit-review.md](docs/cycle/plan12-exit-review.md)
- **Kickoff:** [plan12-kickoff.md](docs/cycle/plan12-kickoff.md) (2026-07-03)
- **Opvolger:** `plan13.md` gestart 2026-07-03

## Relatie met eerdere plannen

- Vorige plan: `plan11.md`
- Gebruik: verdieping in retrievalkwaliteit, rankingstrategie en explainability.
- Regel: als dit plan volledig is afgevinkt, ga verder in `plan13.md`.

## Waar zitten we nu

- [x] Alle werkstromen AA–AD afgerond
- [x] Plan12 exit review + plan13 kickoff (2026-07-03)

## Hoofddoelen plan12

- [x] Retrievalkwaliteit verder verhogen (MRR + recall op long-tail)
- [x] Explainability en reproduceerbaarheid verbeteren
- [x] Query-routing intelligentie verfijnen

## Werkstroom AA - Reranking (EXP-002)

- [x] Reranker A/B experiment opzetten — `reranker_models.yaml` + `RERANKER_VARIANT`
- [x] MRR/latency benchmark script — `run-reranker-ab-eval.sh`
- [x] Promotie of rollback documenteren in experiment-backlog — control default behouden

## Werkstroom AB - Explainability

- [x] Retrieval score breakdown in API-response — `retrieval_explainability` + citation scores
- [x] Route rationale (`hybrid`, `live_fallback`, taal) standaardiseren — `RetrievalExplainability`
- [x] Frontend bronpaneel uitbreiden met score/route metadata — `RetrievalExplainabilityPanel`

## Werkstroom AC - Query routing

- [x] Intentbibliotheek uitbreiden — `query_intent_library.yaml` + loader
- [x] Domain-clustering voor lage-confidence queries — `DomainClusterService`
- [x] Router unit tests + eval cases voor edge intents — `run-router-intent-eval.sh`

## Werkstroom AD - Long-tail eval

- [x] Long-tail fixture (`rag_eval_longtail.json`) — 20 edge-case vragen
- [x] Benchmark script `run-longtail-eval.sh`
- [x] Drempel in `eval-thresholds.yaml` — recall@5 ≥ 0.75

## KPI-doelen plan12

- [x] MRR +0.05 vs baseline (EXP-002) — ceiling 1.0; control behouden
- [x] p95 query latency < 10s — ~1.3s gemeten
- [x] Long-tail recall@5 ≥ 0.75 — 0.95 gemeten

## Exit criteria plan12

- [x] Werkstromen AA t/m AD afgerond
- [x] Meetbare kwaliteitswinst bewezen
- [x] Go voor `plan13.md` — [plan13-kickoff.md](docs/cycle/plan13-kickoff.md) APPROVED

## Overdrachtsregel naar plan13

- [x] Plan13 gestart na plan12 exit review — [plan12-exit-review.md](docs/cycle/plan12-exit-review.md)

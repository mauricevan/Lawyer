# Implementatieplan Deel 12 - Geavanceerde retrieval intelligence


## Implementatiestatus (2026-07-03)

- **Status:** Kickoff goedgekeurd — zie [plan12-kickoff.md](docs/cycle/plan12-kickoff.md)
- **Exit review vorig plan:** [plan11-exit-review.md](docs/cycle/plan11-exit-review.md)
- **Thema's:** [next-cycle-themes.yaml](docs/cycle/next-cycle-themes.yaml)
- **ADR:** [0005-retrieval-intelligence-plan12.md](docs/adr/0005-retrieval-intelligence-plan12.md)
- **Vorige plan:** `plan11.md` (afgerond 2026-07-03)

## Relatie met eerdere plannen

- Vorige plan: `plan11.md`
- Gebruik: verdieping in retrievalkwaliteit, rankingstrategie en explainability.
- Regel: als dit plan volledig is afgevinkt, ga verder in `plan13.md`.

## Waar zitten we nu

- [x] `plan11.md` volledig afgerond
- [x] Kwaliteitsverbeteringstraject gestart (kickoff 2026-07-03)
- [x] Eval baseline 1.0 + CI integration gate live

## Hoofddoelen plan12

- [ ] Retrievalkwaliteit verder verhogen (MRR + recall op long-tail)
- [ ] Explainability en reproduceerbaarheid verbeteren
- [ ] Query-routing intelligentie verfijnen

## Werkstroom AA - Reranking (EXP-002)

- [x] Reranker A/B experiment opzetten — `reranker_models.yaml` + `RERANKER_VARIANT`
- [x] MRR/latency benchmark script — `run-reranker-ab-eval.sh`
- [x] Promotie of rollback documenteren in experiment-backlog — control default behouden

## Werkstroom AB - Explainability

- [x] Retrieval score breakdown in API-response — `retrieval_explainability` + citation scores
- [x] Route rationale (`hybrid`, `live_fallback`, taal) standaardiseren — `RetrievalExplainability`
- [x] Frontend bronpaneel uitbreiden met score/route metadata — `RetrievalExplainabilityPanel`

## Werkstroom AC - Query routing

- [ ] Intentbibliotheek uitbreiden (`query_router_service`)
- [ ] Domain-clustering voor lage-confidence queries
- [ ] Router unit tests + eval cases voor edge intents

## Werkstroom AD - Long-tail eval

- [ ] Long-tail fixture (`rag_eval_longtail.json`)
- [ ] Benchmark script `run-longtail-eval.sh`
- [ ] Drempel in `eval-thresholds.yaml`

## KPI-doelen plan12

- [ ] MRR +0.05 vs baseline (EXP-002 success metric)
- [ ] p95 query latency < 10s na reranker change
- [ ] Long-tail recall@5 ≥ 0.75

## Exit criteria plan12

- [ ] Werkstromen AA t/m AD afgerond
- [ ] Meetbare kwaliteitswinst bewezen (eval + experiment outcome)
- [ ] Go voor `plan13.md`

## Overdrachtsregel naar plan13

- [ ] Plan13 start na plan12 exit review + portfolio board

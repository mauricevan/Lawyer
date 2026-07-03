# Implementatieplan Deel 11 - Langetermijn schaal en internationale uitbreiding


## Implementatiestatus (2026-07-03)

- **Status:** Afgerond — zie [plan11-exit-review.md](docs/cycle/plan11-exit-review.md)
- **Kickoff:** [plan11-kickoff.md](docs/cycle/plan11-kickoff.md) (2026-07-02)
- **Opvolger:** `plan12.md` gestart 2026-07-03

## Relatie met eerdere plannen

- Vorige plan: `plan10.md`
- Gebruik: gecontroleerde uitbreiding naar nieuwe landen, talen en use-cases.
- Regel: als dit plan volledig is afgevinkt, ga verder in `plan12.md`.

## Waar zitten we nu

- [x] `plan10.md` volledig afgerond
- [x] Volgende groeifase formeel gestart (kickoff 2026-07-02)
- [x] Internationale kwaliteit boven fallback-niveau (native corpus + eval 1.0)
- [x] Plan11 exit review + plan12 kickoff (2026-07-03)

## Hoofddoelen plan11

- [x] Internationale domeinuitbreiding uitvoeren — employment `go` (AB); sustainability blijft `pilot`
- [x] Meertalige kwaliteit op niveau houden — eval 1.0 FR/DE/ES
- [x] Juridische dekking gecontroleerd vergroten — compliance docs + check script

## Werkstroom AA - Taal en corpus

- [x] Native FR/DE/ES corpus ingest (EXP-001) — `multilingual_seed.yaml`, `ingest_multilingual_seed.py`
- [x] Multilingual eval baseline verhogen — threshold 0.85 in `eval-thresholds.yaml`
- [x] Terminologie/glossary per taal documenteren — `terminology-glossary.yaml`

## Werkstroom AB - Domeinuitbreiding

- [x] Employment domein `pilot` → `go` — cluster `employment_law`, 3 richtlijnen
- [x] Domain benchmark opnieuw draaien — recall@5 1.0
- [x] Eval fixture bijwerken — seed-prioriteit in `build_eval_fixture.py`

## Werkstroom AC - Compliance

- [x] Nationale implementatie gaps documenteren — `national-implementation-gaps.yaml`
- [x] Product-limitations per taal bijwerken — `product-limitations.yaml` + frontend
- [x] Legal escalation pad valideren — `run-legal-compliance-check.sh`

## Werkstroom AD - CI hardening

- [x] Integration eval in CI (TD-004) — `integration-eval` job + `run-integration-eval-gate.sh`
- [x] Release pipeline stack-aware eval — `run-stack-aware-eval.sh` + release-gate workflow

## KPI-doelen plan11

- [x] Multilingual recall ≥ 0.85 (native corpus) — gemeten 1.0/1.0
- [x] Employment domain benchmark pass — 1.0 recall@5 (9 vragen)
- [x] TD-004 closed — integration eval on every PR

## Exit criteria plan11

- [x] Werkstromen AA t/m AD afgerond
- [x] Kwaliteitsdrempels gehaald — release + CI eval 1.0
- [x] Go voor `plan12.md` — [plan12-kickoff.md](docs/cycle/plan12-kickoff.md) APPROVED

## Overdrachtsregel naar plan12

- [x] Plan12 gestart na plan11 exit review — [plan11-exit-review.md](docs/cycle/plan11-exit-review.md)

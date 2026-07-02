# Implementatieplan Deel 11 - Langetermijn schaal en internationale uitbreiding


## Implementatiestatus (2026-07-02)

- **Status:** Kickoff goedgekeurd — zie [plan11-kickoff.md](docs/cycle/plan11-kickoff.md)
- **Thema's:** [next-cycle-themes.yaml](docs/cycle/next-cycle-themes.yaml)
- **Vorige plan:** `plan10.md` (cycle + transition live)

## Relatie met eerdere plannen

- Vorige plan: `plan10.md`
- Gebruik: gecontroleerde uitbreiding naar nieuwe landen, talen en use-cases.
- Regel: als dit plan volledig is afgevinkt, ga verder in `plan12.md`.

## Waar zitten we nu

- [x] `plan10.md` volledig afgerond
- [x] Volgende groeifase formeel gestart (kickoff 2026-07-02)
- [x] Internationale kwaliteit boven fallback-niveau (native corpus + eval 1.0)

## Hoofddoelen plan11

- [ ] Internationale domeinuitbreiding uitvoeren
- [ ] Meertalige kwaliteit op niveau houden
- [ ] Juridische dekking gecontroleerd vergroten

## Werkstroom AA - Taal en corpus

- [x] Native FR/DE/ES corpus ingest (EXP-001) — `multilingual_seed.yaml`, `ingest_multilingual_seed.py`
- [x] Multilingual eval baseline verhogen — threshold 0.85 in `eval-thresholds.yaml`
- [x] Terminologie/glossary per taal documenteren — `terminology-glossary.yaml`

## Werkstroom AB - Domeinuitbreiding

- [ ] Employment domein `pilot` → `go`
- [ ] Domain benchmark opnieuw draaien
- [ ] Eval fixture bijwerken

## Werkstroom AC - Compliance

- [ ] Nationale implementatie gaps documenteren
- [ ] Product-limitations per taal bijwerken
- [ ] Legal escalation pad valideren

## Werkstroom AD - CI hardening

- [ ] Integration eval in CI (TD-004)
- [ ] Release pipeline stack-aware eval

## KPI-doelen plan11

- [x] Multilingual recall ≥ 0.85 (native corpus) — gemeten 1.0/1.0
- [ ] Employment domain benchmark pass
- [ ] TD-004 closed

## Exit criteria plan11

- [ ] Werkstromen AA t/m AD afgerond
- [ ] Kwaliteitsdrempels gehaald
- [ ] Go voor `plan12.md`

## Overdrachtsregel naar plan12

- [ ] Plan12 start na plan11 exit review + portfolio board

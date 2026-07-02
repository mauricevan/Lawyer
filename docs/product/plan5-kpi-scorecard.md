# Plan5 KPI-scorecard & exit-criteria

**Periode:** Q3 2026 (jul–sep 2026)  
**Laatste snapshot:** 2026-07-02  
**Eigenaar:** product + engineering  
**Bron metrics:** [portfolio-metrics.yaml](./portfolio-metrics.yaml)

---

## 1. KPI-definities

| ID | KPI | Formule | Target | Floor | Meetfrequentie | Bron |
|---|---|---|---|---|---|---|
| `retrieval_quality` | Recall@5 | eval fixture hits / vragen | ≥ 0.80 | 0.75 | Per release | `./scripts/qa/run-retrieval-eval.sh` |
| `multilingual_quality` | FR/DE/ES Recall@5 | per taal gemiddelde | ≥ 0.70 | 0.65 | Per release | `./scripts/qa/run-multilingual-eval.sh` |
| `domain_coverage` | Go-domeinen pass | aantal domeinen met `decision=pass` | 5 | 5 | Per release | `./scripts/qa/run-domain-benchmark.sh` |
| `regression_rate` | Release regressies | releases met eval-fail / totaal releases | ≤ 0.10 | 0.20 | Per release | release gate + post-release review |
| `positive_feedback_score` | Gem. feedbackrating | `AVG(rating)` over kwartaal | ≥ 4.0 | 3.5 | Maandelijks | DB `query_feedback` |
| `negative_feedback_ratio` | Negatieve share | `COUNT(rating≤3) / COUNT(*)` | ≤ 0.15 | 0.25 | Maandelijks | DB `query_feedback` |
| `citation_reliability` | Citation coverage | `citation_coverage_rate` admin metrics | ≥ 0.85 | 0.75 | Per release | `GET /api/v1/admin/metrics` |
| `query_latency_p95` | Query p95 (s) | Prometheus histogram | < 8 | < 10 | Wekelijks | Grafana / Prometheus |
| `availability` | Ready success rate | successful `/ready` / totaal | ≥ 0.995 | 0.99 | Wekelijks | Prometheus |

### Trendregels (plan5 KPI-doelen)

| Doel | Trend | Minimale data |
|---|---|---|
| Gebruikersfeedback score stijgt QoQ | `positive_feedback_score` Q(n) > Q(n-1) | ≥ 30 feedback entries per kwartaal |
| Negatieve feedbackratio daalt | `negative_feedback_ratio` dalend over 3 maanden | ≥ 30 feedback entries per kwartaal |
| Nieuwe domeinen halen drempel | Elk `go`-domein `recall_at_5 ≥ min` in registry | Benchmark per domein-release |
| Regressies binnen grens | `regression_rate ≤ floor` | ≥ 3 releases in kwartaal |

---

## 2. Snapshot Q3 2026 — 2026-07-02

| KPI | Waarde | Status | Toelichting |
|---|---|---|---|
| `retrieval_quality` | *niet gemeten in snapshot* | ⏳ Meet bij volgende release | Draai eval tegen geïndexeerde corpus |
| `multilingual_quality` | Fixture 15 vragen; unit groen | ✅ Instrument klaar | Integratie-eval vereist live stack |
| `domain_coverage` | 5 go-domeinen gedefinieerd | ✅ Registry | Benchmark bij re-index |
| `regression_rate` | 0 releases met eval-gate fail (Q3) | ⏳ Baseline start Q3 | Eerste productierelease telt mee |
| `positive_feedback_score` | *geen productiedata* | ⏳ Wacht op pilot | DB leeg / geen publieke pilot |
| `negative_feedback_ratio` | *geen productiedata* | ⏳ Wacht op pilot | Zie [feedback-triage.md](./feedback-triage.md) |
| `citation_reliability` | In-process snapshot | ⏳ Na deploy meten | `citation_reliability_service` actief |
| `query_latency_p95` | *geen prod Prometheus* | ⏳ Lokaal OK | Stack via `docker-compose.local.yml` |
| `availability` | *geen prod SLA-data* | ⏳ Lokaal OK | `/ready` checks in verify-stack |

**Legenda:** ✅ gehaald of instrumentatie klaar · ⏳ baseline / wacht op data · ❌ onder floor

---

## 3. Exit-criteria plan5 — beoordeling

| Criterium | Status | Bewijs / mitigatie |
|---|---|---|
| Werkstromen H, I, J afgerond | ✅ | Alle checkboxes in [plan5.md](../../plan5.md) |
| Kwartaaldoelen gehaald of herpland | ⏳ Mitigatie | KPI's 4–9 wachten op pilot; technische KPI's via release gate ([mitigatieplan](#5-mitigatieplan-q3-2026)) |
| Continue verbetercyclus operationeel | ✅ | Wekelijkse feedback-triage, release checklist, kwartaal portfolio review, architecture review gepland |
| `plan4.md` volledig afgerond | ⏳ | Technisch ~95%; open: verwijderingsverzoeken, log-integriteit, formele sign-off ([plan4-exit-gap.md](./plan4-exit-gap.md)) |
| Governance/security actief | ✅ | CI security-scan, secret-scan, RBAC, runbooks, rotation tabletop |
| Teamcapaciteit groeifase | ⏳ | Solo-capaciteit; capacity model 50/20/15/15 documented |

### Overdracht naar plan6

Plan6 mag starten wanneer:

1. ✅ Werkstromen H/I/J af — **ja**
2. ⏳ Minimaal één kwartaal KPI-review uitgevoerd — **gepland eind Q3 2026**
3. ⏳ Productie- of pilot-feedback baseline vastgelegd — **mitigatie Q3 week 8**

---

## 4. Meetritme

| Ritme | Actie | Output |
|---|---|---|
| **Per release** | `run-release-checklist.sh` + eval scripts | Post-release review metrics-tabel |
| **Wekelijks** | Feedback triage (maandag) | Weekly product note |
| **Maandelijks** | KPI SQL + admin metrics | Rij in scorecard §2 bijwerken |
| **Per kwartaal** | `run-quarterly-portfolio-review.sh` + architecture review | Besluitenlog + roadmap Q+1 |

### Feedback SQL (handmatig tot TD-010)

```sql
-- Negatieve ratio (laatste 30 dagen)
SELECT
  COUNT(*) FILTER (WHERE rating <= 3)::float / NULLIF(COUNT(*), 0) AS negative_ratio,
  AVG(rating)::numeric(4,2) AS mean_rating,
  COUNT(*) AS total
FROM query_feedback
WHERE created_at >= NOW() - INTERVAL '30 days';

-- Per categorie
SELECT category, COUNT(*), AVG(rating)
FROM query_feedback
WHERE created_at >= NOW() - INTERVAL '30 days'
GROUP BY category
ORDER BY COUNT(*) DESC;
```

### Automatische snapshot

```bash
./scripts/ops/run-plan5-kpi-snapshot.sh
```

---

## 5. Mitigatieplan Q3 2026

| Risico | Mitigatie | Deadline | Owner |
|---|---|---|---|
| Geen feedbackdata | Start beperkte pilot (5–10 gebruikers) + triage | Q3 wk 4 | product |
| Eval niet in CI | TD-004: integration eval in release-gate | Q3 wk 8 | backend |
| plan4 niet formeel signed off | [plan4-exit-gap.md](./plan4-exit-gap.md) afwerken | Q3 wk 6 | engineering |
| KPI dashboard ontbreekt | TD-010: admin feedback metrics endpoint | Q4 2026 | backend |

---

## 6. Kwartaalreview checklist (eind Q3)

- [ ] §2 snapshot bijgewerkt met echte waarden
- [ ] Trend QoQ berekend voor feedback (indien ≥30 entries)
- [ ] Alle `go`-domeinen benchmark groen
- [ ] `regression_rate` berekend over Q3 releases
- [ ] Mitigaties uit §5 afgerond of herpland in [quarterly-roadmap.md](./quarterly-roadmap.md)
- [ ] Besluit: plan6 starten ja/nee → vastleggen in architecture review log

---

## 7. Hoofddoelen plan5 — eindbeoordeling

| Hoofddoel | Status | Bewijs |
|---|---|---|
| Productwaarde via gebruikersdata | ⏳ Instrumentatie klaar; data volgt pilot | Feedback API, triage, scorecard |
| Domeinen/talen gecontroleerd | ✅ | domain-registry, language-registry, benchmarks |
| Continue verbetercyclus | ✅ | H1/H2/J1/J2 + runbooks + portfolio review |

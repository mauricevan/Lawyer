# Baseline audit — Declarant workflow (iteratie 0)

**Datum:** 2026-07-06  
**Branch:** uncommitted iteration-1 work

## Synthetic chunk audit (Qdrant)

Script: `python3 backend/scripts/audit_synthetic_chunks.py`

| CELEX | Totaal | Synthetic | Status |
|-------|--------|-----------|--------|
| 32011L0083 Consumer Rights | 4 | 4 | ❌ 100% placeholder |
| 32014R0910 eIDAS | 4 | 4 | ❌ 100% placeholder |
| 32022R2065 DSA | 20 | 0 | ✅ echte tekst |
| 32013R0952 UCC | 20 | 0 | ✅ echte tekst |
| 32004L0038 Burgerschap | 0 | 0 | ❌ niet geïngest |

**Conclusie:** I1 kan geen adequate grounded answer geven tot re-ingest eIDAS + 2004/38.

## Scenario baseline (vóór fixes)

| ID | Routing | Antwoord | Probleem |
|----|---------|----------|----------|
| I1 legitimatie + overheid | consumer ❌ | Consumer Rights synthetic | verkeerde route + nep-tekst |
| D1 platform + contentwebsite | consumer ❌ → DSA ✅ | gap → adequate | routing gefixt iteratie 0 |
| C1 douane webshop | consumer ❌ | — | nog niet getest |

## Iteratie 1 fixes applied

- Synthetic chunk detector + evidence filter
- `identity_verification_issue` + `customs_import_issue` conflicts
- `customs_law` domain
- 32004L0038 toegevoegd aan curated_celex (re-ingest pending)
- Acceptance tests `tests/acceptance/test_declarant_scenarios.py`

## Volgende iteratie (1b)

1. Re-ingest eIDAS + 2004/38 met live EUR-Lex (geen fallback)
2. Quarantaine/remove synthetic Consumer Rights chunks
3. National-law boundary block in layperson answers (I1)
4. Her-run acceptance → iteration-log update

# Top 20 foutpatronen — mitigaties (plan5 H2)

| # | Patroon | Mitigatie in codebase |
|---|---|---|
| 1 | Dunne live EUR-Lex 202-response | `fallback_subdivisions.py` + confidence penalty |
| 2 | Lage retrieval score | `AnswerConfidenceService` + verificatievragen |
| 3 | Geen bronnen bij antwoord | `AnswerPolicyService.enforce_citations` |
| 4 | Verkeerde CELEX in filter | Pydantic CELEX pattern + `validate_celex` |
| 5 | Prompt injection | `GuardrailsService` |
| 6 | SSRF via live fetch | `ssrf_guard.py` host allowlist |
| 7 | Inconsistente citations | `SourceConsistencyService` |
| 8 | Oude vs geconsolideerde versie | `TrustIndicatorService.prefer_consolidated` |
| 9 | Dubbele chunks in context | `context_dedup.py` |
| 10 | Zwakke domein-router | `QueryRouterService` + legal term hints |
| 11 | Cache met verouderde chunks | TTL + `cache_cleanup_service` |
| 12 | Onzeker compliance-antwoord | Verificatievragen bij `query_mode=compliance` |
| 13 | Vergelijkingsvragen onvolledig | Extra verificatie bij `compare` mode |
| 14 | Leek-modus zonder CELEX in tekst | Bronnen in apart paneel + disclaimer |
| 15 | LLM hallucineert buiten context | Strikte system prompts + fallback answer |
| 16 | Retrieval timeout | `RetrievalBudget` + graceful degrade |
| 17 | BM25/vector mismatch | Hybrid RRF fusion |
| 18 | Feedback zonder categorie | Taxonomie in `FeedbackPanel` |
| 19 | Geen monitoring per release | `CitationReliabilityService` in `/admin/metrics` |
| 20 | Gebruiker weet niet wanneer escaleren | `VerificationQuestions` + `/juridische-informatie` |

## Release-monitoring

Na elke deploy: controleer `GET /api/v1/admin/metrics` → `citation_reliability.citation_coverage_rate` ≥ 0.9.

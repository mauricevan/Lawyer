# Blueprint → codebase mapping

Companion to [eu-regulation-blueprint.md](./eu-regulation-blueprint.md).  
Status: **2026-07-03** — production stack largely implements the blueprint; gaps below are tracked explicitly.

## Architecture (§2)

| Blueprint block | Implementation |
|---|---|
| Frontend | `frontend/src/app/page.tsx`, `ChatThread`, `CitationSources` |
| Intent / query processing | `question_intent_service.py`, `query_router_service.py`, `VagueQuestionService` |
| Vector index (kennisbank) | Qdrant + PostgreSQL FTS; ingest via `ingestion/scripts/ingest_curated.py` |
| Live EUR-Lex | `live_retrieval_service.py`, `CellarRestClient`, `SparqlClient` |
| RAG engine | `retrieval_pipeline_service.py` (dense + BM25 + RRF + rerank) |
| LLM answer | `llm_service.py`, `answer_bundle_service.py`, `shared/config/prompts.yaml` |
| Layperson topics (80+) | `layperson_topic_service.py`, `shared/config/layperson_topics/` |

## Component checklist (§3–§7)

| Requirement | Status | Location / notes |
|---|---|---|
| Article-level chunks + CELEX metadata | ✅ | `ingestion/src/indexer.py`, chunk schema |
| Priority-1 CELEX in corpus config | ✅ | `curated_celex.yaml` — DWU cluster added in blueprint build |
| Run ingest after CELEX add | ⚙️ | `python ingestion/scripts/ingest_curated.py --from-celex 32013R0952` |
| Live fallback when local miss | ✅ | `enable_live_fallback`, `live_retrieval_service.py` |
| Reranking | ✅ | `RerankerService` |
| System prompt + structure | ✅ | `prompts.yaml` (layperson + professional + specific variants) |
| Temperature ≤ 0.2 | ✅ | `settings.llm_temperature` (default 0.1) |
| EUR-Lex links in citations | ✅ | `CitationBuilderService`, `TrustCard` |
| Disclaimer on every page | ✅ | `LegalFooter`, response `disclaimer` field |
| Trust / provenance banner | ✅ | `AnswerProvenance.tsx` |
| Escalation path | ✅ | `legalDisclaimers.ts`, `/juridische-informatie` |
| Feedback | ✅ | `FeedbackPanel` |
| Domain selector | ✅ | `QueryFilterControls`, `GuidedQuerySelector` |

## Flow (§8)

End-to-end path: `POST /api/v1/query` → `RagService.query` → router → retrieval pipeline → `AnswerBundleService.build` → topic template **or** LLM **or** gap.

Intent routing rules: [eu-regulation-qa-bot-system-instruction.md](./eu-regulation-qa-bot-system-instruction.md) + `topic_intent_gate_service.py`.

## Guardrails (§11)

| Control | Location |
|---|---|
| Injection / abuse patterns | `query.py` `_enforce_guardrails` |
| No answer without retrieval attempt | `AnswerBundleService`, `context_adequacy_service.py` |
| Specificity guard (no generic UCC intro) | `answer_specificity_guard_service.py` |
| Coverage gaps + referrals | `insufficient_coverage_answer_service.py`, `coverage_guidance.yaml` |

## Quality gates

```bash
export API_URL=http://localhost:8003
bash scripts/qa/run-customer-journey-gate.sh
node scripts/qa/article-specific-audit.mjs "$API_URL"
```

## Roadmap alignment (§13)

| Phase | Blueprint | Project status |
|---|---|---|
| Fase 1 MVP | Corpus + RAG + frontend + disclaimer | ✅ Complete (plan1–plan31) |
| Fase 2 | Rerank, domain selector, live API, feedback | ✅ Mostly complete |
| **Fase 2b** | **Legal source planner + article-targeted fetch** | ✅ [ADR-0009](../adr/0009-agentic-legal-reasoning.md) fase 1 |
| Fase 3 | NL implementation, HvJ, B2B API | 📋 Backlog / quarterly roadmap |

## Ingest new Priority-1 documents

After editing `curated_celex.yaml`:

```bash
cd /home/mau/Desktop/Projecs/Lawyer
set -a && source .env && set +a
PYTHONPATH=. python ingestion/scripts/ingest_curated.py \
  --from-celex 32013R0952 --skip-existing --delay-seconds 2
```

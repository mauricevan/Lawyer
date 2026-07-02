# Engineer onboarding — Lawyer RAG (plan5 J2)

**Doel:** nieuwe engineer binnen 2 werkdagen productief op lokale stack + eerste PR.  
**Laatste update:** 2026-07-02

## Dag 1 — Omgeving

### Vereisten

- Docker, Python 3.12, Node 20, git
- Lees: [AGENTS.md](../../AGENTS.md) (verplicht vóór eerste commit)

### Setup

```bash
git clone git@github.com:mauricevan/Lawyer.git && cd Lawyer
cp .env.example .env
./scripts/security/install-hooks.sh
docker compose -f docker-compose.yml -f docker-compose.local.yml up -d
pip install -r backend/requirements.txt -r ingestion/requirements.txt
cd backend && alembic upgrade head && cd ..
PYTHONPATH=. python ingestion/scripts/seed_corpus.py
uvicorn backend.src.main:app --reload --port 8001
cd frontend && npm install && npm run dev
```

### Verificatie

| Check | Commando | Verwacht |
|---|---|---|
| API health | `curl -s localhost:8001/health` | `200` |
| Ready | `curl -s localhost:8001/ready` | postgres/qdrant ok |
| Frontend | http://localhost:3000 | Chat laadt |
| Tests | `pytest backend/tests -m "not integration" -q` | groen |
| Knowledge base | `./scripts/ops/run-knowledge-base-check.sh` | PASS |

## Dag 2 — Architectuur

### Lagen (lees in deze volgorde)

1. **Query flow:** `backend/src/routes/query.py` → `RagService` → retrieval → `LlmService`
2. **Retrieval:** hybrid RRF (`rag_service.py`), cache, live fallback (`live_retrieval_service.py`)
3. **Data:** `ingestion/` pipeline, `curated_celex.yaml`, Qdrant + Postgres FTS
4. **Security:** `ssrf_guard.py`, JWT/RBAC (`dependencies/auth.py`), input validation
5. **Product:** disclaimers, feedback, confidence/verification (`answer_quality_service.py`)

### Belangrijke docs

| Onderwerp | Pad |
|---|---|
| Runbooks | [runbook-index.md](./runbook-index.md) |
| Troubleshooting | [troubleshooting.md](./troubleshooting.md) |
| Pair review | [pair-review-policy.md](./pair-review-policy.md) |
| Incident learnings | [incident-learnings.md](./incident-learnings.md) |
| ADR's | [../adr/README.md](../adr/README.md) |
| SLO's | [../ops/slo-definition.md](../ops/slo-definition.md) |
| Domeinen | [../product/domain-selection-framework.md](../product/domain-selection-framework.md) |
| Talen | [../product/language-rollout.md](../product/language-rollout.md) |

## Eerste bijdrage (checklist)

- [ ] Eén bugfix of doc-fix op branch `fix/...`
- [ ] Tests toegevoegd of bijgewerkt
- [ ] `./scripts/ops/check-pair-review.sh` als kritieke paden geraakt
- [ ] `./scripts/ops/run-release-checklist.sh` lokaal groen
- [ ] Commit met Conventional Commits (`feat:`, `fix:`, `docs:`)

## Solo-team pair review

Bij geen tweede reviewer: volg [pair-review-policy.md](./pair-review-policy.md) — gestructureerde self-review + `PAIR_REVIEW_ACK=yes`.

## Escalatie

Zie [escalation-matrix.md](../ops/escalation-matrix.md).

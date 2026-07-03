# ADR-0006: Plan13 document lifecycle automation

**Status:** Accepted  
**Date:** 2026-07-03  
**Context:** Plan12 closed with stable retrieval eval. Corpus freshness and version drift are the primary operational risk.

## Decision

1. **Plan13** focuses on document lifecycle automation, not new retrieval features.
2. **Staleness** is measured via `modified_at` vs `indexed_at` on `documents` table.
3. **Reindex** reuses existing ingest scripts (`ingest_curated.py --force-reindex`, `run-reindex.sh`).
4. **Deprecation** uses an explicit registry before hard deletes; archive-first policy.

## Consequences

- New lifecycle services live under `backend/src/services/` and `ingestion/scripts/`.
- Eval gates remain mandatory before promoting reindex policy changes.
- Sustainability domain promotion deferred until lifecycle metrics are operational.

# Document lifecycle — states and archive flow (plan13 AC)

## Lifecycle states

| State | Indexed | Default search | Ingest |
|---|---|---|---|
| **active** | Yes | Included | Normal |
| **soft_deprecated** | Yes | Excluded | Allowed (audit only) |
| **retired** | Yes | Excluded | Blocked |
| **archived** | Purged | Excluded | Blocked |

Registry: `shared/config/document_deprecation_register.yaml`

## Archive-first policy

1. **Detect** — staleness scan (`run-document-staleness-scan.sh`)
2. **Reindex** — drift repair (`run-lifecycle-reindex.sh`)
3. **Soft-deprecate** — register entry, exclude from default retrieval
4. **Retire** — mark `retired` after product sign-off (no new ingest)
5. **Archive** — optional purge via `purge_document_index` after retention review

No hard delete without register entry and ops approval (ADR-0006).

## Soft-deprecate retrieval rules

- Deprecated CELEX excluded from vector, FTS, BM25 merge, and hint search
- **Explicit CELEX filter** still returns chunks (compliance / audit lookup)
- `include_deprecated: true` on `QueryFilters` bypasses exclusion (admin tooling)

## no_go domain alignment

Domains with `status: no_go` in `domain_registry.yaml` must have seed CELEX
registered before indexed corpus is used in production eval.

Check: `./scripts/platform/run-deprecation-register-check.sh`

## Related runbooks

- [reindex-runbook.md](../ops/reindex-runbook.md)
- [document_lifecycle_policy.yaml](../../shared/config/document_lifecycle_policy.yaml)
- [ADR-0006](../adr/0006-document-lifecycle-plan13.md)

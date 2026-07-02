#!/usr/bin/env bash
# List self-service platform scripts (plan6 K1).
set -euo pipefail

cat <<'EOF'
Lawyer platform self-service scripts (plan6)

  ./scripts/platform/run-reindex.sh          Re-index curated + backfill FTS
  ./scripts/platform/run-backfill-chunks.sh  Qdrant → Postgres chunk text
  ./scripts/platform/run-cache-warmup.sh     Warm query cache (eval fixture)
  ./scripts/platform/check-env-parity.sh     .env.example vs parity matrix

  ./scripts/ops/run-release-pipeline.sh    Release gate + verify + optional eval
  ./scripts/ops/run-error-budget-check.sh    SLO/error budget snapshot
  ./scripts/ops/run-recovery-drill.sh        Recovery drill (health + rollback)

  ./scripts/dev/bootstrap.sh                 Fast local stack bootstrap
  ./scripts/dev/provision-test-data.sh       Seed corpus + eval fixtures
  ./scripts/dev/scaffold-service.sh <Name>   New backend service module

Docs: docs/platform/self-service-ops.md
EOF

#!/usr/bin/env bash
# Create the platform hardening PR (requires: gh auth login).
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"

export PATH="${HOME}/.local/bin:${PATH}"

if ! command -v gh >/dev/null 2>&1; then
  echo "gh not found. Install to ~/.local/bin or apt." >&2
  exit 1
fi

if ! gh auth status >/dev/null 2>&1; then
  echo "Not logged in. Run: gh auth login" >&2
  exit 1
fi

BRANCH="feature/plan3-plan4-platform-hardening"

gh pr create --base main --head "$BRANCH" \
  --title "feat: platform hardening, security governance, and pilot feedback" \
  --body "$(cat <<'EOF'
## Summary

- **Plan3 scale & retrieval:** hybrid RRF/BM25 routing, live EUR-Lex fallback, Redis/DB cache, Celery ingest queues, observability (Prometheus/Grafana), eval gate Recall@5 1.00.
- **Plan4 security & compliance:** JWT/RBAC, SSRF guard, audit trail + retention, data lifecycle, secret inventory/rotation, input validation audit, legal disclaimers, release governance (SLOs, hotfix runbooks).
- **Plan5 pilot:** in-chat feedback UI with taxonomy and triage docs.

## Commits (6)

| Commit | Beschrijving |
|--------|--------------|
| `80f06d1` | Plan3 scale, retrieval quality, plan4 security governance |
| `d749f31` | Plan4 E2 secret inventory & rotation |
| `21b32b6` | Plan4 E3 input validation & pentest remediations |
| `f356912` | Plan5 H1 pilot feedback UI |
| `b08b462` | Plan4 F3 legal disclaimers & source policy |
| `658c996` | Plan4 G release governance & release gate |

## Test plan

- [ ] `./scripts/ops/run-release-checklist.sh`
- [ ] `alembic upgrade head` (migrations 0001–0004)
- [ ] `docker compose -f docker-compose.yml -f docker-compose.local.yml up -d`
- [ ] `./scripts/observability/verify-stack.sh`
- [ ] Smoke: query, feedback, `/juridische-informatie`, admin stats

EOF
)"

echo "PR created. Open with: gh pr view --web"

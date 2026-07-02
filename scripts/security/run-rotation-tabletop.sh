#!/usr/bin/env bash
# Tabletop checklist for secret rotation (no production changes).
set -euo pipefail

cat <<'EOF'
Secret rotation tabletop — vink af in incident ticket

[ ] 1. Identificeer getroffen secret uit secret-inventory.md
[ ] 2. Genereer vervangende waarde (openssl rand / provider dashboard)
[ ] 3. Update secret store / .env in staging eerst
[ ] 4. Rolling restart backend + workers
[ ] 5. Smoke test: /health, /ready, /api/v1/query
[ ] 6. Revoke oude credential bij provider
[ ] 7. Verifieer check-secrets.sh all = groen
[ ] 8. Documenteer in post-mortem / rotatie-log

Zie docs/security/secret-rotation-playbook.md voor details.
EOF

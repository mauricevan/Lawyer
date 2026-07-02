#!/usr/bin/env bash
# Roll back prompt and retrieval config to last committed version (plan7 P).
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"

FILES=(
  shared/config/prompts.yaml
  shared/config/retrieval_params.yaml
)

for file in "${FILES[@]}"; do
  if git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    git checkout HEAD -- "$file"
    echo "Restored: $file"
  else
    echo "FAIL: not a git repository"
    exit 1
  fi
done

echo "PASS: Prompt config rolled back to HEAD"

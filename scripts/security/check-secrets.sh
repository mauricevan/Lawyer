#!/usr/bin/env bash
# Scan repository files for common secret patterns before commit.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"

SCAN_MODE="${1:-staged}"
FAILURES=0

PATTERNS=(
  "sk-or-v1-[A-Za-z0-9_-]{20,}"
  "sk-ant-[A-Za-z0-9_-]{20,}"
  "-----BEGIN (RSA |OPENSSH |EC )?PRIVATE KEY-----"
  "(AKIA|ASIA)[0-9A-Z]{16}"
)

PLACEHOLDER_MARKERS=(
  "your_openrouter_api_key_here"
  "your_anthropic_api_key_here"
  "your_openai_api_key_here"
  "change_me_in_production_use_long_random_string"
  "example"
  "placeholder"
  "changeme"
  "replace_me"
)

is_placeholder() {
  local value="$1"
  local marker
  for marker in "${PLACEHOLDER_MARKERS[@]}"; do
    if [[ "$value" == *"$marker"* ]]; then
      return 0
    fi
  done
  return 1
}

collect_files() {
  case "$SCAN_MODE" in
    staged)
      git diff --cached --name-only --diff-filter=ACMRT
      ;;
    all)
      git ls-files
      ;;
    *)
      echo "Usage: $0 [staged|all]" >&2
      exit 2
      ;;
  esac
}

report_match() {
  local file="$1"
  local line_no="$2"
  local label="$3"
  echo "SECRET RISK: $label in $file:$line_no"
  FAILURES=$((FAILURES + 1))
}

scan_env_assignments() {
  local file="$1"
  local line_no=0
  local line

  while IFS= read -r line || [[ -n "$line" ]]; do
    line_no=$((line_no + 1))
    if [[ "$line" =~ ^[[:space:]]*(OPENROUTER_API_KEY|ANTHROPIC_API_KEY|OPENAI_API_KEY|JWT_SECRET|EU_LOGIN_PASSWORD)[[:space:]]*=[[:space:]]*(.+) ]]; then
      local value="${BASH_REMATCH[2]}"
      value="${value%\"}"
      value="${value#\"}"
      value="${value%\'}"
      value="${value#\'}"
      if [[ -n "$value" && "$value" != "''" && "$value" != '""' ]]; then
        if ! is_placeholder "$value"; then
          report_match "$file" "$line_no" "env assignment with non-placeholder value"
        fi
      fi
    fi
  done < "$file"
}

scan_patterns() {
  local file="$1"
  local pattern
  local matches

  for pattern in "${PATTERNS[@]}"; do
    matches="$(grep -nE "$pattern" "$file" 2>/dev/null || true)"
    if [[ -n "$matches" ]]; then
      while IFS= read -r match_line; do
        [[ -z "$match_line" ]] && continue
        local line_no="${match_line%%:*}"
        report_match "$file" "$line_no" "pattern match ($pattern)"
      done <<< "$matches"
    fi
  done
}

scan_file() {
  local file="$1"
  if [[ ! -f "$file" ]]; then
    return
  fi
  scan_env_assignments "$file"
  scan_patterns "$file"
}

if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  echo "Not a git repository: $ROOT" >&2
  exit 2
fi

if [[ "$SCAN_MODE" == "staged" ]] && git diff --cached --name-only --diff-filter=ACM | grep -qx ".env"; then
  echo "SECRET RISK: .env is staged for commit"
  FAILURES=$((FAILURES + 1))
fi

while IFS= read -r file; do
  [[ -z "$file" ]] && continue
  case "$file" in
    .git/*|node_modules/*|venv/*|.venv/*|data/*|tools/pg_extract/*|__pycache__/*|.next/*|dist/*|htmlcov/*)
      continue
      ;;
  esac
  scan_file "$file"
done < <(collect_files)

if [[ "$FAILURES" -gt 0 ]]; then
  echo
  echo "Secret scan failed with $FAILURES issue(s)."
  echo "Remove secrets, rotate exposed credentials, and use .env.example placeholders."
  exit 1
fi

echo "Secret scan passed ($SCAN_MODE)."

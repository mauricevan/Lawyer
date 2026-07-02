#!/usr/bin/env bash
# Scaffold a new backend service module from template (plan6 M4).
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"

NAME="${1:-}"
if [[ -z "$NAME" ]]; then
  echo "Usage: $0 <ServiceName>"
  exit 1
fi

SNAKE=$(echo "$NAME" | sed 's/\([A-Z]\)/_\1/g' | sed 's/^_//' | tr '[:upper:]' '[:lower:]')
SERVICE_FILE="backend/src/services/${SNAKE}_service.py"
TEST_FILE="backend/tests/test_${SNAKE}_service.py"
TEMPLATE_DIR="docs/engineering/templates/service_module"

if [[ -f "$SERVICE_FILE" ]]; then
  echo "FAIL: $SERVICE_FILE already exists"
  exit 1
fi

mkdir -p backend/src/services backend/tests
sed "s/{{ServiceName}}/${NAME}/g; s/{{service_snake}}/${SNAKE}/g" \
  "$TEMPLATE_DIR/service.py.template" > "$SERVICE_FILE"
sed "s/{{ServiceName}}/${NAME}/g; s/{{service_snake}}/${SNAKE}/g" \
  "$TEMPLATE_DIR/test_service.py.template" > "$TEST_FILE"

echo "Created:"
echo "  $SERVICE_FILE"
echo "  $TEST_FILE"
echo "Next: implement logic + run pytest $TEST_FILE"

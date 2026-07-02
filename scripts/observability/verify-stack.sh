#!/usr/bin/env bash
# Verify Lawyer observability stack: backend /metrics, Prometheus scrape, Grafana dashboard.
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT_DIR"

BACKEND_URL="${BACKEND_URL:-http://127.0.0.1:8000}"
PROMETHEUS_URL="${PROMETHEUS_URL:-http://127.0.0.1:9090}"
GRAFANA_URL="${GRAFANA_URL:-http://127.0.0.1:3001}"
GRAFANA_USER="${GRAFANA_USER:-admin}"
GRAFANA_PASSWORD="${GRAFANA_PASSWORD:-${GRAFANA_ADMIN_PASSWORD:-sloten}}"
DASHBOARD_UID="${DASHBOARD_UID:-lawyer-rag-overview}"

pass() { printf '✅ %s\n' "$1"; }
fail() { printf '❌ %s\n' "$1"; exit 1; }
info() { printf '→ %s\n' "$1"; }

info "Checking backend health at ${BACKEND_URL}/health"
curl -fsS "${BACKEND_URL}/health" >/dev/null || fail "Backend health check failed"
pass "Backend is healthy"

info "Generating sample metrics via /metrics"
METRICS_BODY="$(curl -fsS "${BACKEND_URL}/metrics")"
echo "$METRICS_BODY" | rg -q 'lawyer_queries_total' || fail "lawyer_queries_total missing from /metrics"
pass "Backend exposes lawyer_* Prometheus metrics"

info "Checking Prometheus at ${PROMETHEUS_URL}/-/healthy"
curl -fsS "${PROMETHEUS_URL}/-/healthy" >/dev/null || fail "Prometheus is not reachable"
pass "Prometheus is healthy"

info "Checking Prometheus scrape target lawyer-backend"
TARGET_JSON="$(curl -fsS "${PROMETHEUS_URL}/api/v1/targets")"
echo "$TARGET_JSON" | rg -q '"job":"lawyer-backend"' || fail "lawyer-backend job not found"
echo "$TARGET_JSON" | rg -q '"health":"up"' || fail "lawyer-backend target is not UP"
pass "Prometheus scrapes backend successfully"

info "Checking Grafana health at ${GRAFANA_URL}/api/health"
curl -fsS "${GRAFANA_URL}/api/health" >/dev/null || fail "Grafana is not reachable"
pass "Grafana is healthy"

info "Checking Grafana datasource Prometheus"
DATASOURCES="$(curl -fsS -u "${GRAFANA_USER}:${GRAFANA_PASSWORD}" \
  "${GRAFANA_URL}/api/datasources/name/Prometheus")"
echo "$DATASOURCES" | rg -q '"type":"prometheus"' || fail "Prometheus datasource missing"
pass "Grafana Prometheus datasource is provisioned"

info "Checking dashboard uid=${DASHBOARD_UID}"
DASHBOARD="$(curl -fsS -u "${GRAFANA_USER}:${GRAFANA_PASSWORD}" \
  "${GRAFANA_URL}/api/dashboards/uid/${DASHBOARD_UID}")"
echo "$DASHBOARD" | rg -q '"title":"Lawyer RAG Overview"' || fail "Dashboard not found"
pass "Grafana dashboard 'Lawyer RAG Overview' is loaded"

info "Querying Prometheus for lawyer_queries_total"
QUERY_JSON="$(curl -fsS --get "${PROMETHEUS_URL}/api/v1/query" \
  --data-urlencode 'query=lawyer_queries_total')"
echo "$QUERY_JSON" | rg -q '"status":"success"' || fail "Prometheus query failed"
pass "Prometheus can query lawyer metrics"

printf '\nAll observability checks passed.\n'
printf 'Grafana dashboard: %s/d/%s\n' "$GRAFANA_URL" "$DASHBOARD_UID"

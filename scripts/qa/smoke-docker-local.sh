#!/usr/bin/env bash
# Smoke test for docker-compose.local stack (:8001 backend, :3000 frontend).
set -euo pipefail

API_URL="${API_URL:-http://localhost:8001}"
FRONTEND_URL="${FRONTEND_URL:-http://localhost:3000}"
CHATBOT_Q="Moet ik mijn chatbot registreren bij de overheid?"

echo "== Health =="
curl -fsS --max-time 10 "${API_URL}/health" >/dev/null
curl -fsS --max-time 10 "${API_URL}/ready" >/dev/null

echo "== Sync query smoke (TC02) =="
response="$(curl -fsS --max-time 60 -X POST "${API_URL}/api/v1/query" \
  -H "Content-Type: application/json" \
  -d "{\"question\":\"${CHATBOT_Q}\",\"language\":\"nl\",\"audience\":\"layperson\",\"query_mode\":\"compliance\"}")"
echo "${response}" | python3 -c "
import json, sys
data = json.load(sys.stdin)
answer = data.get('answer', '')
assert data.get('answer'), 'missing answer'
assert 'coverage_status' in data, 'missing coverage_status'
assert 'misschien' not in answer.lower(), 'stale misschien in answer'
assert 'none' not in answer.lower(), 'artikel None in answer text'
if data.get('coverage_status') == 'adequate':
    assert data.get('citations'), 'adequate without citations'
    assert any('32024' in (c.get('celex') or '') for c in data['citations']), 'missing AI Act CELEX'
print('coverage_status:', data.get('coverage_status'))
"

echo "== Stream metadata smoke (TC12) =="
stream_body="$(curl -fsS --max-time 90 -N -X POST "${API_URL}/api/v1/query/stream" \
  -H "Content-Type: application/json" \
  -d "{\"question\":\"Mag ik dit?\",\"language\":\"nl\",\"audience\":\"layperson\"}")"
conv_id="$(echo "${stream_body}" | python3 -c "
import json, sys
conv_id = ''
for line in sys.stdin:
    line = line.strip()
    if not line.startswith('data:'):
        continue
    event = json.loads(line[5:].strip())
    if event.get('step') == 'complete':
        conv_id = event.get('detail', {}).get('conversation_id') or conv_id
print(conv_id)
")"
if [[ -z "${conv_id}" ]]; then
  echo "Stream did not return conversation_id" >&2
  exit 1
fi
curl -fsS --max-time 10 "${API_URL}/api/v1/conversations/${conv_id}" | python3 -c "
import json, sys
data = json.load(sys.stdin)
assistant = next(m for m in data['messages'] if m['role'] == 'assistant')
meta = assistant.get('metadata') or {}
assert meta.get('coverage_status') == 'clarify_only', meta
assert meta.get('verification_questions'), 'missing verification_questions in metadata'
print('stream metadata OK for', data['id'])
"

echo "== OJ citation smoke (2658/87) =="
oj_response="$(curl -fsS --max-time 90 -X POST "${API_URL}/api/v1/query" \
  -H "Content-Type: application/json" \
  -d '{"question":"Ben je bekend met Verordening (EEG) nr. 2658/87?","language":"nl","audience":"layperson"}')"
echo "${oj_response}" | python3 -c "
import json, sys
data = json.load(sys.stdin)
status = data.get('coverage_status')
assert status != 'insufficient', f'unexpected insufficient: {status}'
citations = data.get('citations') or []
celexes = [c.get('celex') or '' for c in citations]
if status == 'adequate':
    assert any('31987R2658' in c for c in celexes), celexes
print('coverage_status:', status)
"

echo "== Modern OJ citation smoke (952/2013) =="
modern_response="$(curl -fsS --max-time 90 -X POST "${API_URL}/api/v1/query" \
  -H "Content-Type: application/json" \
  -d '{"question":"Ben je bekend met Verordening (EU) nr. 952/2013?","language":"nl","audience":"layperson"}')"
echo "${modern_response}" | python3 -c "
import json, sys
data = json.load(sys.stdin)
status = data.get('coverage_status')
assert status != 'insufficient', f'unexpected insufficient: {status}'
citations = data.get('citations') or []
celexes = [c.get('celex') or '' for c in citations]
if status == 'adequate':
    assert any('32013R0952' in c for c in celexes), celexes
print('coverage_status:', status)
"

echo "== Frontend reachability =="
curl -fsS --max-time 10 -o /dev/null "${FRONTEND_URL}"

echo "Smoke docker local: OK"

#!/usr/bin/env bash
# Validate .env.example parity with platform matrix (plan6 K4).
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"

python3 - <<'PY'
import sys
from pathlib import Path

import yaml

example = Path(".env.example")
matrix = yaml.safe_load(Path("docs/platform/env-parity-matrix.yaml").read_text(encoding="utf-8"))
keys = set()
for line in example.read_text(encoding="utf-8").splitlines():
    line = line.strip()
    if not line or line.startswith("#") or "=" not in line:
        continue
    keys.add(line.split("=", 1)[0].strip())

missing = [key for key in matrix.get("required_all", []) if key not in keys]
if missing:
    print("FAIL: .env.example missing keys:", ", ".join(missing))
    sys.exit(1)

print(f"OK: {len(keys)} keys in .env.example")
print(f"OK: {len(matrix.get('required_all', []))} required keys present")
for env in ("staging_overrides", "production_overrides"):
    overrides = matrix.get(env, {})
    print(f"OK: {env} documents {len(overrides)} overrides")
PY

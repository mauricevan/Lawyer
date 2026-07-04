#!/usr/bin/env node
/** Shared fetch for layperson audit scripts with optional audit token. */
export function auditHeaders() {
  const headers = { "Content-Type": "application/json" };
  const token = process.env.AUDIT_RUN_TOKEN || "";
  if (token) headers["X-Audit-Token"] = token;
  return headers;
}

export async function auditQuery(base, question, audience = "layperson", queryMode = "open") {
  for (let attempt = 0; attempt < 4; attempt += 1) {
    const res = await fetch(`${base}/api/v1/query`, {
      method: "POST",
      headers: auditHeaders(),
      body: JSON.stringify({ question, audience, query_mode: queryMode }),
    });
    if (res.status === 429) {
      await new Promise((r) => setTimeout(r, 4000 * (attempt + 1)));
      continue;
    }
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return res.json();
  }
  throw new Error("HTTP 429");
}

export function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

#!/usr/bin/env node
/**
 * Agent flow smoke — verifies interpretation_plan and articles_fetched in SSE complete event.
 * Usage: node scripts/qa/agent-flow-smoke.mjs [baseUrl]
 */
import { sleep } from "./audit-fetch.mjs";

const BASE = process.argv[2] || process.env.API_URL || "http://localhost:8003";
const QUESTION =
  "Wanneer moet een stof worden geregistreerd volgens de REACH-verordening (Verordening (EG) nr. 1907/2006)?";

async function streamQuery(baseUrl, question) {
  const res = await fetch(`${baseUrl}/api/v1/query/stream`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      question,
      audience: "professional",
      query_mode: "open",
      language: "nl",
    }),
  });
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  const text = await res.text();
  const events = text
    .split("\n\n")
    .filter((block) => block.startsWith("data: "))
    .map((block) => JSON.parse(block.slice(6)));
  return events;
}

function assertAgentMetadata(completeDetail) {
  const issues = [];
  if (completeDetail.retrieval_route !== "agent_flow") {
    issues.push(`route=${completeDetail.retrieval_route}, expected agent_flow`);
  }
  if (!completeDetail.interpretation_plan) {
    issues.push("missing interpretation_plan");
  }
  const explain = completeDetail.retrieval_explainability || {};
  if (!explain.resolved_celex?.length && !completeDetail.interpretation_plan?.instruments?.length) {
    issues.push("no resolved_celex in explainability");
  }
  if (!Array.isArray(explain.articles_fetched)) {
    issues.push("articles_fetched not in explainability");
  }
  return issues;
}

async function main() {
  console.log(`Agent flow smoke → ${BASE}\n`);
  await sleep(500);
  const events = await streamQuery(BASE, QUESTION);
  const steps = events.map((e) => e.step);
  const required = ["planning", "resolving", "fetching", "verifying", "complete"];
  const missingSteps = required.filter((s) => !steps.includes(s));
  if (missingSteps.length) {
    console.log("FAIL missing SSE steps:", missingSteps.join(", "));
    process.exit(1);
  }
  const complete = events.find((e) => e.step === "complete");
  const issues = assertAgentMetadata(complete.detail || {});
  if (issues.length) {
    console.log("FAIL metadata");
    issues.forEach((x) => console.log(`  ↳ ${x}`));
    process.exit(1);
  }
  console.log("PASS agent-flow smoke");
  console.log(`  steps: ${steps.join(" → ")}`);
  console.log(`  route: ${complete.detail.retrieval_route}`);
}

main().catch((err) => {
  console.error("ERROR", err.message || err);
  process.exit(1);
});

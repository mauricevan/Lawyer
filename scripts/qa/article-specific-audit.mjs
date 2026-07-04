#!/usr/bin/env node
/**
 * Article-specific CI checks — docs/product/eu-regulation-qa-bot-system-instruction.md §7.4
 * Usage: node scripts/qa/article-specific-audit.mjs [baseUrl] [--json]
 */
import { parseAuditArgs, checkSemanticRules } from "./layperson-audit-lib.mjs";
import { auditQuery, sleep } from "./audit-fetch.mjs";

const { base: BASE, jsonOut } = parseAuditArgs(process.argv);
const DELAY_MS = 4000;

const CASES = [
  {
    id: "AS-01",
    question:
      "Mag een bedrijf een invoeraangifte wijzigen nadat de goederen zijn vrijgegeven? Noem de relevante artikelen.",
    audience: "professional",
    query_mode: "compliance",
    must_mention: ["164", "vrijgave", "verzoek"],
    must_not_contain: ["moderniseert douaneprocessen", "TARIC", "expediteur bij complexe zendingen"],
    allow_gap: true,
    gap_must_contain: ["kon geen specifieke wettekst worden gevonden"],
  },
  {
    id: "AS-02",
    question:
      "Binnen welke termijn moet ik een verzoek tot terugbetaling van douanerechten indienen?",
    audience: "professional",
    query_mode: "compliance",
    must_mention: ["121", "drie jaar"],
    must_not_contain: ["moderniseert douaneprocessen"],
    allow_gap: true,
  },
  {
    id: "AS-03",
    question: "Welke EU-artikelen regelen quantum teleportatie in douane-entrepots?",
    audience: "professional",
    query_mode: "compliance",
    expect_gap: true,
    gap_must_contain: ["kon geen specifieke wettekst worden gevonden"],
    must_not_contain: ["moderniseert douaneprocessen"],
  },
];

function scoreCase(testCase, data) {
  const issues = checkSemanticRules(data, testCase);
  const answer = (data.answer || "").toLowerCase();
  if (testCase.expect_gap) {
    return ["insufficient", "irrelevant"].includes(data.coverage_status) ? "GOED" : "SLECHT";
  }
  if (testCase.allow_gap && ["insufficient", "irrelevant"].includes(data.coverage_status)) {
    const gapNeed = testCase.gap_must_contain || [];
    return gapNeed.every((term) => answer.includes(term.toLowerCase())) ? "GOED" : "SLECHT";
  }
  if (issues.length) return "SLECHT";
  if (answer.includes("wettelijke grondslag") || answer.includes("art.")) return "GOED";
  return testCase.must_mention?.length ? "SLECHT" : "GOED";
}

async function main() {
  const results = [];
  let good = 0;
  if (!jsonOut) console.log(`Article-specific audit → ${BASE}\n`);
  for (let i = 0; i < CASES.length; i += 1) {
    const tc = CASES[i];
    if (i > 0) await sleep(DELAY_MS);
    if (!jsonOut) process.stdout.write(`${tc.id} … `);
    try {
      const data = await auditQuery(BASE, tc.question, tc.audience, tc.query_mode);
      const clarity = scoreCase(tc, data);
      if (!jsonOut) console.log(clarity);
      if (clarity === "GOED") good += 1;
      results.push({ ...tc, clarity, coverage: data.coverage_status, route: data.retrieval_route });
    } catch (err) {
      if (!jsonOut) console.log("ERROR");
      results.push({ ...tc, clarity: "ERROR", error: err.message });
    }
  }
  const threshold = CASES.length;
  if (jsonOut) {
    console.log(JSON.stringify({ set: "AS", good, total: CASES.length, threshold, results }, null, 2));
  } else {
    console.log(`\nGOED: ${good}/${CASES.length}`);
  }
  if (good < threshold) process.exit(1);
}

main();

#!/usr/bin/env node
/**
 * Breadth smoke: diverse EUR-Lex question types against /api/v1/query
 * Usage: node scripts/qa/eurlex-breadth-smoke.mjs [baseUrl]
 */
import { auditQuery, sleep } from "./audit-fetch.mjs";

const BASE = process.argv[2] || process.env.API_URL || "http://localhost:8003";
const DELAY_MS = 2500;

const CASES = [
  {
    id: "TC-CUSTOMS-01",
    category: "customs_hint_live",
    question:
      "Als ik een paard van zuiver ras importeer onder goederen code 0101 - is de kans dan groot dat deze goederencode juist is?",
    expect: { coverage: "adequate", celexIncludes: "31987R2658", routeIncludes: ["live_fallback", "hybrid", "cache", "cn_classification", "layperson_topic"] },
  },
  {
    id: "TC-CUSTOMS-02",
    category: "customs_oj_citation",
    question: "Wat regelt Verordening (EEG) nr. 2658/87?",
    expect: { coverage: "adequate", celexIncludes: "31987R2658", routeIncludes: ["live_fallback", "hybrid", "cache", "cn_classification", "layperson_topic"] },
  },
  {
    id: "TC-AI-01",
    category: "corpus_ai_act",
    question: "Moet ik mijn chatbot registreren bij de overheid?",
    expect: { coverage: "adequate", celexIncludes: "32024R1689" },
  },
  {
    id: "TC-PRIV-01",
    category: "corpus_gdpr",
    question: "Mag mijn werkgever mijn e-mails lezen onder de AVG?",
    expect: { coverage: "adequate", celexIncludes: "32016R0679" },
  },
  {
    id: "TC-FIN-01",
    category: "corpus_dora",
    question: "Wat is DORA en voor welke financiële instellingen geldt het?",
    expect: { coverage: "adequate", celexIncludes: "32022R2554" },
  },
  {
    id: "TC-CELEX-01",
    category: "explicit_celex",
    question: "Wat zijn de belangrijkste verplichtingen in CELEX 32022R2554?",
    expect: { coverage: "adequate", celexIncludes: "32022R2554" },
  },
  {
    id: "TC-LIVE-01",
    category: "live_fallback_whistleblower",
    question: "Wat verplicht de EU-whistleblower-richtlijn werkgevers te doen bij meldingen?",
    expect: { coverage: "adequate", minConfidence: 0.1 },
  },
  {
    id: "TC-GAP-01",
    category: "national_law_gap",
    question: "Hoeveel vakantiedagen heb ik volgens de Nederlandse wet?",
    expect: { coverageIncludes: ["insufficient", "irrelevant"] },
  },
  {
    id: "TC-CLARIFY-01",
    category: "vague_clarify",
    question: "Mag ik dit?",
    expect: { coverage: "clarify_only" },
  },
  {
    id: "TC-TRANSPORT-01",
    category: "eurlex_discovery_stress",
    question: "Welke EU-verordening regelt de aansprakelijkheid van vervoerders bij internationaal goederenvervoer?",
    expect: { minAnswerLen: 80 },
  },
];

async function query(question, audience = "layperson") {
  return auditQuery(BASE, question, audience, "compliance");
}

function celexes(citations = []) {
  return citations.map((c) => c.celex).filter(Boolean);
}

function check(caseDef, data) {
  const issues = [];
  const exp = caseDef.expect;
  const cov = data.coverage_status;
  const route = data.retrieval_route;
  const cxs = celexes(data.citations);
  const conf = data.confidence_score ?? 0;

  if (exp.coverage && cov !== exp.coverage) issues.push(`coverage_status=${cov}, expected ${exp.coverage}`);
  if (exp.coverageIncludes && !exp.coverageIncludes.includes(cov)) {
    issues.push(`coverage_status=${cov}, expected one of ${exp.coverageIncludes.join("|")}`);
  }
  if (exp.celexIncludes && !cxs.some((c) => c.includes(exp.celexIncludes))) {
    issues.push(`citations ${JSON.stringify(cxs)}, expected CELEX containing ${exp.celexIncludes}`);
  }
  if (exp.routeIncludes && route && !exp.routeIncludes.includes(route)) {
    issues.push(`retrieval_route=${route}, expected one of ${exp.routeIncludes.join("|")}`);
  }
  if (exp.minConfidence != null && conf < exp.minConfidence) {
    issues.push(`confidence=${conf} below ${exp.minConfidence}`);
  }
  if (exp.minAnswerLen && (data.answer || "").length < exp.minAnswerLen) {
    issues.push(`answer too short (${(data.answer || "").length} chars)`);
  }
  if ((data.answer || "").toLowerCase().includes("buiten wat ik betrouwbaar")) {
    if (exp.coverage === "adequate") issues.push("answer looks like coverage-gap template");
  }
  return issues;
}

async function main() {
  console.log(`EUR-Lex breadth smoke → ${BASE}\n`);
  const results = [];
  for (let i = 0; i < CASES.length; i += 1) {
    const tc = CASES[i];
    if (i > 0) await sleep(DELAY_MS);
    process.stdout.write(`${tc.id} … `);
    try {
      const data = await query(tc.question);
      const issues = check(tc, data);
      const status = issues.length ? "FAIL" : "PASS";
      console.log(status);
      results.push({
        id: tc.id,
        category: tc.category,
        status,
        coverage_status: data.coverage_status,
        retrieval_route: data.retrieval_route,
        confidence: data.confidence_score,
        celexes: celexes(data.citations),
        issues,
        answer_preview: (data.answer || "").slice(0, 120).replace(/\n/g, " "),
      });
    } catch (err) {
      console.log("ERROR");
      results.push({ id: tc.id, category: tc.category, status: "ERROR", error: String(err.message || err) });
    }
  }

  console.log("\n--- Summary ---");
  const pass = results.filter((r) => r.status === "PASS").length;
  const fail = results.filter((r) => r.status === "FAIL").length;
  const err = results.filter((r) => r.status === "ERROR").length;
  console.log(`PASS ${pass} / FAIL ${fail} / ERROR ${err} / total ${results.length}\n`);

  for (const r of results) {
    console.log(
      `${r.status.padEnd(5)} ${r.id} [${r.category}] cov=${r.coverage_status ?? "-"} route=${r.retrieval_route ?? "-"} celex=${JSON.stringify(r.celexes ?? [])}`,
    );
    if (r.issues?.length) r.issues.forEach((i) => console.log(`       ↳ ${i}`));
    if (r.error) console.log(`       ↳ ${r.error}`);
    if (r.answer_preview) console.log(`       ↳ ${r.answer_preview}…`);
  }

  process.exit(fail + err > 0 ? 1 : 0);
}

main();

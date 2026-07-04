#!/usr/bin/env node
/**
 * Answer quality smoke: content assertions, not just CELEX routing.
 * Usage: node scripts/qa/answer-quality-smoke.mjs [baseUrl]
 */
import { auditQuery, sleep } from "./audit-fetch.mjs";

const BASE = process.argv[2] || process.env.API_URL || "http://localhost:8003";
const DELAY_MS = 2500;

function isWeakAnswer(text) {
  const t = (text || "").toLowerCase();
  return [
    "kan dit niet bevestigen",
    "geen informatie",
    "geen antwoord",
    "buiten wat ik",
    "artikel none",
  ].some((p) => t.includes(p));
}

const CASES = [
  {
    id: "AQ-01",
    question:
      "Als ik een paard van zuiver ras importeer onder goederen code 0101 - is de kans dan groot dat deze goederencode juist is?",
    assert: (d) =>
      d.coverage_status === "adequate" &&
      (d.answer || "").includes("0101") &&
      ((d.answer || "").includes("0101 21 00") || (d.answer || "").includes("010121")) &&
      !isWeakAnswer(d.answer),
  },
  {
    id: "AQ-02",
    question: "Ben je bekend met Verordening (EEG) nr. 2658/87?",
    assert: (d) =>
      d.coverage_status === "adequate" &&
      /nomenclatuur|tarief|douane/i.test(d.answer || ""),
  },
  {
    id: "AQ-03",
    question: "Moet ik mijn chatbot registreren bij de overheid?",
    assert: (d) =>
      d.coverage_status === "adequate" &&
      (d.answer || "").length > 120 &&
      !isWeakAnswer(d.answer),
  },
  {
    id: "AQ-04",
    question: "Mag mijn werkgever mijn e-mails lezen onder de AVG?",
    assert: (d) => !/none/i.test(d.answer || ""),
  },
  {
    id: "AQ-05",
    question: "Wat is DORA en voor welke financiële instellingen geldt het?",
    assert: (d) =>
      d.coverage_status === "adequate" &&
      /financ|ict|weerbaar/i.test(d.answer || ""),
  },
  {
    id: "AQ-06",
    question: "Hoeveel vakantiedagen heb ik volgens de Nederlandse wet?",
    assert: (d, res) => res.ok && ["insufficient", "irrelevant"].includes(d.coverage_status),
  },
  {
    id: "AQ-07",
    question: "Mag ik dit?",
    assert: (d) => d.coverage_status === "clarify_only",
  },
  {
    id: "AQ-08",
    question: "Wat zijn de belangrijkste verplichtingen in CELEX 32022R2554?",
    assert: (d) =>
      d.coverage_status === "adequate" &&
      (d.answer || "").length > 100 &&
      !/lijkt artikel \(onbekend\) relevant/i.test(d.answer || ""),
  },
  {
    id: "AQ-09",
    question: "Wat regelt Verordening (EU) nr. 952/2013?",
    assert: (d) =>
      d.coverage_status === "adequate" &&
      /douane|customs|wetboek/i.test(d.answer || ""),
  },
  {
    id: "AQ-10",
    question: "Mag ik klantgegevens gebruiken om mijn AI te trainen?",
    assert: (d) => d.coverage_status === "adequate" && !isWeakAnswer(d.answer),
  },
  {
    id: "AQ-11",
    question: "Wat is Verordening (EU) 2016/679?",
    assert: (d) =>
      d.coverage_status === "adequate" &&
      /persoonsgegevens|privacy|avg|gdpr/i.test(d.answer || ""),
  },
  {
    id: "AQ-12",
    question: "Geldt de AI-wet ook voor mijn kleine webshop?",
    assert: (d) => d.coverage_status === "adequate" && !isWeakAnswer(d.answer),
  },
  {
    id: "AQ-13",
    question: "Wat regelt CELEX 31987R2658?",
    assert: (d) =>
      d.coverage_status === "adequate" &&
      (d.citations || []).some((c) => (c.celex || "").includes("31987R2658")),
  },
  {
    id: "AQ-14",
    question: "Vergelijk GDPR artikel 6 met artikel 9",
    audience: "professional",
    query_mode: "compare",
    assert: (d) => d.coverage_status !== "adequate" || (d.citations || []).length >= 1,
  },
  {
    id: "AQ-15",
    question: "Welke EU-verordening regelt de gecombineerde nomenclatuur voor douane?",
    assert: (d) =>
      d.coverage_status === "adequate" &&
      !isWeakAnswer(d.answer) &&
      (d.citations || []).some((c) => (c.celex || "").includes("31987")),
  },
];

async function query(caseDef) {
  const data = await auditQuery(
    BASE,
    caseDef.question,
    caseDef.audience || "layperson",
    caseDef.query_mode || "compliance",
  );
  return { data, res: { ok: true } };
}

async function main() {
  let passed = 0;
  for (let i = 0; i < CASES.length; i += 1) {
    const testCase = CASES[i];
    if (i > 0) await sleep(DELAY_MS);
    try {
      const { data, res } = await query(testCase);
      if (testCase.assert(data, res)) {
        console.log(`PASS ${testCase.id}`);
        passed += 1;
      } else {
        console.error(`FAIL ${testCase.id}`, {
          coverage: data.coverage_status,
          preview: (data.answer || "").slice(0, 180),
        });
      }
    } catch (err) {
      console.error(`FAIL ${testCase.id}`, err.message);
    }
  }
  console.log(`Answer quality smoke: ${passed}/${CASES.length}`);
  console.log("Note: restart backend (uvicorn without --reload) before running smoke tests.");
  if (passed < 12) process.exit(1);
}

main();

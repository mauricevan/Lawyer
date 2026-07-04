#!/usr/bin/env node
/**
 * Maturity RAG audit — EU questions that must work WITHOUT layperson topic templates.
 * Uses professional audience or phrasing outside topic patterns.
 * Usage: node scripts/qa/maturity-rag-audit.mjs [baseUrl]
 */
import { auditQuery, sleep } from "./audit-fetch.mjs";

const BASE = process.argv[2] || process.env.API_URL || "http://localhost:8003";
const DELAY_MS = 3000;

const CASES = [
  {
    id: "MR-01",
    audience: "professional",
    question:
      "Op welke rechtsgronden kan een organisatie persoonsgegevens verwerken zonder toestemming volgens AVG artikel 6?",
    expect: { coverage: "adequate", celexIncludes: "32016R0679", forbidRoute: "layperson_topic" },
  },
  {
    id: "MR-02",
    audience: "professional",
    question:
      "Hoe lang bedraagt de herroepingstermijn voor een overeenkomst op afstand volgens Richtlijn 2011/83/EU artikel 9?",
    expect: { coverage: "adequate", celexIncludes: "32011L0083", answerIncludes: "14" },
  },
  {
    id: "MR-03",
    audience: "professional",
    question:
      "Welke informatie moet een fabrikant opnemen in de EU-conformiteitsverklaring volgens Verordening 2019/1020?",
    expect: { coverage: "adequate", celexIncludes: "32019R1020" },
  },
  {
    id: "MR-04",
    audience: "layperson",
    question:
      "Wat staat in artikel 9 lid 1 van Richtlijn 2011/83/EU over de bedenktijd bij online aankopen?",
    expect: { coverage: "adequate", celexIncludes: "32011L0083", answerIncludes: "14" },
  },
  {
    id: "MR-05",
    audience: "professional",
    question: "Noem de kernverplichtingen uit CELEX 32022R2554 (DORA) voor financiële entiteiten.",
    expect: { coverage: "adequate", celexIncludes: "32022R2554" },
  },
  {
    id: "MR-06",
    audience: "professional",
    question:
      "Welke EU-verordening regelt de aansprakelijkheid van vervoerders bij internationaal goederenvervoer?",
    expect: { minAnswerLen: 120, forbidGap: true },
  },
  {
    id: "MR-07",
    audience: "layperson",
    question:
      "Mag een verwerkingsverantwoordelijke mijn gegevens verwerken op basis van gerechtvaardigd belang onder de AVG?",
    expect: { coverage: "adequate", celexIncludes: "32016R0679" },
  },
  {
    id: "MR-08",
    audience: "professional",
    question: "Wat vereist Verordening (EU) 2024/1689 (AI Act) voor high-risk AI-systemen in artikel 9?",
    expect: { coverage: "adequate", celexIncludes: "32024R1689" },
  },
  {
    id: "MR-09",
    audience: "layperson",
    question: "Hoeveel vakantiedagen heb ik volgens puur Nederlandse arbeidswetgeving?",
    expect: { coverageIncludes: ["insufficient", "irrelevant"] },
  },
  {
    id: "MR-10",
    audience: "professional",
    question:
      "Binnen welke termijn moet een importeur een verzoek tot terugbetaling van invoerrechten indienen volgens het UCC?",
    expect: { coverage: "adequate", celexIncludes: "32013R0952" },
  },
  {
    id: "MR-11",
    audience: "layperson",
    question:
      "Als ik een paard importeer onder code 0101 — welke EU-regeling bepaalt of die code klopt?",
    expect: { coverage: "adequate", celexIncludes: "31987R2658" },
  },
  {
    id: "MR-12",
    audience: "professional",
    question: "Welke artikelen van Verordening 2016/679 regelen het recht op dataportabiliteit?",
    expect: { coverage: "adequate", celexIncludes: "32016R0679", answerIncludes: "20" },
  },
  {
    id: "MR-13",
    audience: "professional",
    question:
      "Welke verplichtingen legt de Europese Milieuaansprakelijkheidsrichtlijn op aan exploitanten die milieuschade veroorzaken?",
    expect: { coverage: "adequate", celexIncludes: "32004L0035", forbidGap: true },
  },
  {
    id: "MR-14",
    audience: "professional",
    question: "Wat vereist de CSRD-richtlijn (2022/2464) van ondernemingen voor duurzaamheidsrapportering?",
    expect: { coverage: "adequate", celexIncludes: "32022L2464", minAnswerLen: 100 },
  },
  {
    id: "MR-15",
    audience: "professional",
    question: "Welke bescherming biedt de EU-klokkenluidersrichtlijn 2024/1385 aan melders?",
    expect: { coverage: "adequate", celexIncludes: "32024L1385", forbidGap: true },
  },
  {
    id: "MR-16",
    audience: "professional",
    question: "Welke verplichtingen stelt de EU-verpakkingsverordening 2024/1780 aan producenten?",
    expect: { minAnswerLen: 100, forbidGap: true },
  },
  {
    id: "MR-17",
    audience: "professional",
    question: "Wat regelt de EU-ecodesignrichtlijn 2009/125 over energieverbruik van producten?",
    expect: { minAnswerLen: 100, forbidGap: true },
  },
  {
    id: "MR-18",
    audience: "professional",
    question:
      "Welke due-diligenceverplichtingen legt Verordening 2024/1681 (CSDDD) op voor milieu en mensenrechten?",
    expect: { coverage: "adequate", celexIncludes: "32024R1681", forbidGap: true },
  },
  {
    id: "MR-19",
    audience: "professional",
    question:
      "Wanneer moet een stof worden geregistreerd volgens de REACH-verordening (Verordening (EG) nr. 1907/2006)?",
    expect: { coverage: "adequate", celexIncludes: "32006R1907", forbidGap: true },
  },
];

const MIN_PASS = Math.ceil(CASES.length * 0.9);

function check(caseDef, data) {
  const issues = [];
  const exp = caseDef.expect;
  const cov = data.coverage_status;
  const route = data.retrieval_route || "";
  const answer = data.answer || "";
  const cxs = (data.citations || []).map((c) => c.celex).filter(Boolean);

  if (exp.coverage && cov !== exp.coverage) issues.push(`coverage=${cov}, expected ${exp.coverage}`);
  if (exp.coverageIncludes && !exp.coverageIncludes.includes(cov)) {
    issues.push(`coverage=${cov}, expected one of ${exp.coverageIncludes.join("|")}`);
  }
  if (exp.celexIncludes && !cxs.some((c) => c.includes(exp.celexIncludes))) {
    issues.push(`celex ${JSON.stringify(cxs)}, expected ${exp.celexIncludes}`);
  }
  if (exp.answerIncludes && !answer.includes(exp.answerIncludes)) {
    issues.push(`answer missing "${exp.answerIncludes}"`);
  }
  if (exp.minAnswerLen && answer.length < exp.minAnswerLen) {
    issues.push(`answer too short (${answer.length})`);
  }
  if (exp.forbidRoute && route === exp.forbidRoute) {
    issues.push(`route=${route} forbidden for RAG maturity case`);
  }
  if (exp.forbidGap && /geen betrouwbaar antwoord|kon geen specifieke wettekst/i.test(answer)) {
    issues.push("gap-like answer forbidden");
  }
  return issues;
}

async function main() {
  console.log(`Maturity RAG audit → ${BASE}\n`);
  let pass = 0;
  for (let i = 0; i < CASES.length; i += 1) {
    const tc = CASES[i];
    if (i > 0) await sleep(DELAY_MS);
    process.stdout.write(`${tc.id} … `);
    try {
      const data = await auditQuery(BASE, tc.question, tc.audience || "professional", "open");
      const issues = check(tc, data);
      if (issues.length) {
        console.log("FAIL");
        issues.forEach((x) => console.log(`       ↳ ${x}`));
        console.log(`       route=${data.retrieval_route} cov=${data.coverage_status}`);
      } else {
        console.log("PASS");
        pass += 1;
      }
    } catch (err) {
      console.log("ERROR");
      console.log(`       ↳ ${err.message || err}`);
    }
  }
  console.log(`\nPASS ${pass}/${CASES.length} (min ${MIN_PASS})`);
  if (pass < MIN_PASS) process.exit(1);
}

main();

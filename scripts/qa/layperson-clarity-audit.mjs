#!/usr/bin/env node
/**
 * Layperson clarity audit — site promise gate:
 * "Uw vraag over EU-regels, helder uitgelegd"
 * Usage: node scripts/qa/layperson-clarity-audit.mjs [baseUrl] [--json]
 * Exit 1 when GOED < 14/20
 */
import { isHeldereUitgelegd, parseAuditArgs } from "./layperson-audit-lib.mjs";
import { auditQuery, sleep } from "./audit-fetch.mjs";

const { base: BASE, jsonOut } = parseAuditArgs(process.argv);
const GOED_THRESHOLD = 14;
const DELAY_MS = 3500;

const CASES = [
  {
    id: "L01",
    theme: "privacy_social",
    question:
      "Mijn buurman filmt mij met zijn drone boven mijn tuin. Mag dat volgens Europese privacyregels?",
    expectEu: true,
  },
  {
    id: "L02",
    theme: "ai_recruitment",
    question:
      "Een bedrijf gebruikt AI om sollicitaties te sorteren. Welke EU-regels moeten zij dan volgen?",
    expectEu: true,
  },
  {
    id: "L03",
    theme: "consumer_warranty",
    question:
      "Ik kocht online een kapotte wasmachine uit Duitsland. Hoe lang garantie heb ik volgens EU-recht?",
    expectEu: true,
  },
  {
    id: "L04",
    theme: "travel_compensation",
    question:
      "Mijn vlucht binnen Europa had 5 uur vertraging. Heb ik recht op compensatie volgens EU-regels?",
    expectEu: true,
  },
  {
    id: "L05",
    theme: "cookies_website",
    question:
      "Moet elke website in Europa een cookiebanner tonen? Wat zegt de EU daarover?",
    expectEu: true,
  },
  {
    id: "L06",
    theme: "cross_border_health",
    question:
      "Kan ik met mijn Nederlandse zorgverzekering een behandeling in België laten betalen via EU-regels?",
    expectEu: true,
  },
  {
    id: "L07",
    theme: "environment_packaging",
    question:
      "Welke EU-regels gelden voor plastic verpakkingen en statiegeld?",
    expectEu: true,
  },
  {
    id: "L08",
    theme: "customs_gift",
    question:
      "Ik krijg een cadeau per post uit de VS boven de 150 euro. Moet ik invoerrechten betalen volgens EU-douane?",
    expectEu: true,
  },
  {
    id: "L09",
    theme: "employment_parental",
    question:
      "Hoeveel weken ouderschapsverlof minimum biedt EU-recht aan vaders?",
    expectEu: true,
  },
  {
    id: "L10",
    theme: "banking_withdrawal",
    question:
      "Mag mijn bank mijn rekening zomaar sluiten? Wat beschermt mij volgens EU-regels?",
    expectEu: true,
  },
  {
    id: "L11",
    theme: "crypto_mica",
    question:
      "Verkoopt een app crypto aan particulieren. Welke EU-regels gelden daarvoor sinds 2024?",
    expectEu: true,
  },
  {
    id: "L12",
    theme: "accessibility",
    question:
      "Moet mijn webshop toegankelijk zijn voor blinden volgens EU-regelgeving?",
    expectEu: true,
  },
  {
    id: "L13",
    theme: "product_safety",
    question:
      "Ik vond glasscherven in een pot voedsel uit Spanje. Welke EU-regels beschermen consumenten?",
    expectEu: true,
  },
  {
    id: "L14",
    theme: "data_portability",
    question:
      "Kan ik van Spotify naar een andere muziekdienst al mijn playlists meenemen onder de AVG?",
    expectEu: true,
  },
  {
    id: "L15",
    theme: "national_only",
    question: "Wat is het wettelijk minimumloon in Nederland per 2026?",
    expectEu: false,
  },
  {
    id: "L16",
    theme: "too_vague",
    question: "Is dit strafbaar?",
    expectEu: null,
  },
  {
    id: "L17",
    theme: "import_car",
    question:
      "Ik importeer een elektrische auto uit Duitsland. Welke EU-regels gelden voor typegoedkeuring?",
    expectEu: true,
  },
  {
    id: "L18",
    theme: "scams_consumer",
    question:
      "Ik ben opgelicht via een webshop in Polen. Kan ik via EU-regels mijn geld terugvorderen?",
    expectEu: true,
  },
  {
    id: "L19",
    theme: "energy_label",
    question:
      "Moet een verhuurder het energielabel aan mij geven volgens EU-regels?",
    expectEu: true,
  },
  {
    id: "L20",
    theme: "deepfake",
    question:
      "Iemand plaatste mijn gezicht in een deepfake-video online. Helpt de EU AI Act mij daartegen?",
    expectEu: true,
  },
];

function scoreAnswer(testCase, data) {
  const cov = data.coverage_status;
  const issues = [];
  const strengths = [];

  if (testCase.expectEu === false) {
    if (["insufficient", "irrelevant"].includes(cov)) strengths.push("eerlijke_gap_niet_eu");
    else issues.push(`verwacht gap voor puur nationaal, kreeg ${cov}`);
  } else if (testCase.expectEu === null) {
    if (cov === "clarify_only") strengths.push("vraagt_om_verduidelijking");
    else issues.push(`verwacht clarify_only, kreeg ${cov}`);
  } else if (isHeldereUitgelegd(data)) {
    strengths.push("helder_uitgelegd");
  } else if (cov === "adequate") {
    issues.push("adequaat_maar_niet_helder");
  } else {
    issues.push(`geen_adequate_eu_antwoord (${cov})`);
  }

  if (cov === "adequate" && !(data.citations || []).length) {
    issues.push("geen_bronverwijzing");
  }

  const clarity =
    strengths.includes("helder_uitgelegd") ||
    (testCase.expectEu === false && strengths.includes("eerlijke_gap_niet_eu")) ||
    (testCase.expectEu === null && strengths.includes("vraagt_om_verduidelijking"))
      ? "GOED"
      : issues.length <= 1 && strengths.length >= 1
        ? "MATIG"
        : "SLECHT";

  return { clarity, issues, strengths };
}

async function main() {
  const rows = [];
  if (!jsonOut) {
    console.log(`Layperson clarity audit → ${BASE}`);
    console.log(`Gate: ≥${GOED_THRESHOLD}/20 GOED (streng rubric)\n`);
  }
  for (let i = 0; i < CASES.length; i += 1) {
    const tc = CASES[i];
    if (i > 0) await sleep(DELAY_MS);
    if (!jsonOut) process.stdout.write(`${tc.id} … `);
    try {
      const data = await auditQuery(BASE, tc.question);
      const scored = scoreAnswer(tc, data);
      if (!jsonOut) console.log(scored.clarity);
      rows.push({
        ...tc,
        ...scored,
        coverage: data.coverage_status,
        route: data.retrieval_route,
        celex: [...new Set((data.citations || []).map((c) => c.celex).filter(Boolean))].slice(0, 3),
        preview: (data.answer || "").slice(0, 160).replace(/\n/g, " "),
      });
    } catch (e) {
      if (!jsonOut) console.log("ERROR");
      rows.push({ ...tc, clarity: "ERROR", issues: [String(e.message)], preview: "" });
    }
  }

  const good = rows.filter((r) => r.clarity === "GOED").length;
  if (jsonOut) {
    console.log(JSON.stringify({ set: "L", good, total: rows.length, threshold: GOED_THRESHOLD, results: rows }, null, 2));
  } else {
    console.log(`\n=== Score vs "helder uitgelegd" ===`);
    console.log(`GOED: ${good}/${rows.length} (drempel ${GOED_THRESHOLD})\n`);
    for (const r of rows) {
      console.log(`${r.clarity.padEnd(6)} ${r.id} [${r.theme}] cov=${r.coverage || "-"}`);
      if (r.issues?.length) console.log(`       ⚠ ${r.issues.join("; ")}`);
      if (r.preview) console.log(`       → ${r.preview}…`);
      console.log("");
    }
    console.log("Note: restart backend (uvicorn without --reload) before running this audit.");
  }
  if (good < GOED_THRESHOLD) process.exit(1);
}

main();

#!/usr/bin/env node
/**
 * Fresh layperson audit — monthly V-set, strict scoring.
 * Usage: node scripts/qa/layperson-fresh-audit.mjs [baseUrl] [--json]
 */
import { isHeldereUitgelegd, parseAuditArgs } from "./layperson-audit-lib.mjs";
import { auditQuery, sleep } from "./audit-fetch.mjs";

const { base: BASE, jsonOut } = parseAuditArgs(process.argv);
const GOED_THRESHOLD = 13;
const DELAY_MS = 3500;

const CASES = [
  { id: "V01", question: "Mag mijn werkgever mijn privé-e-mail lezen op een zakelijke laptop volgens EU-regels?", expectGap: false },
  { id: "V02", question: "Ik koop software met abonnement. Mag de verkoper updates stoppen en toch doorrekenen volgens EU-recht?", expectGap: false },
  { id: "V03", question: "Mijn creditcardgegevens zijn gelekt door een webshop. Kan ik chargeback doen onder EU-recht?", expectGap: false },
  { id: "V04", question: "Moet een winkel camerabeelden van klanten bewaren volgens EU privacyregels?", expectGap: false },
  { id: "V05", question: "Ik verkoop handgemaakte sieraden via Etsy aan andere EU-landen. Moet ik CE-markering hebben?", expectGap: false },
  { id: "V06", question: "Mag een zorgverzekeraar mij weigeren vanwege een oude medische aandoening volgens EU-regels?", expectGap: false },
  { id: "V07", question: "Kan een uitzendbureau mij minder betalen dan vaste collega's voor hetzelfde werk volgens EU-recht?", expectGap: false },
  { id: "V08", question: "Moet een restaurant allergenen vermelden op het menu volgens EU-regels?", expectGap: false },
  { id: "V09", question: "Ik kocht een defecte elektrische fiets in Frankrijk. Heb ik 2 jaar garantie volgens EU-recht?", expectGap: false },
  { id: "V10", question: "Mag Spotify mijn account permanent blokkeren zonder uitleg volgens EU-regels?", expectGap: false },
  { id: "V11", question: "Hoeveel liter wijn mag ik belastingvrij meenemen uit Frankrijk naar Nederland volgens EU-regels?", expectGap: false },
  { id: "V12", question: "Moet een Airbnb-verhuurder mij het energielabel tonen volgens EU-regels?", expectGap: false },
  { id: "V13", question: "Wat is de minimumleeftijd voor een TikTok-account volgens EU-regels?", expectGap: false },
  { id: "V14", question: "Mag mijn werkgever vingerafdruk-scannen voor inklokken volgens de AVG?", expectGap: false },
  { id: "V15", question: "Ik huur een auto in Spanje en weiger hem vanwege krassen. Heb ik recht op terugbetaling volgens EU-recht?", expectGap: false },
  { id: "V16", question: "Hoeveel jaar celstraf krijg je voor belastingfraude in België volgens Belgisch recht?", expectGap: true },
  { id: "V17", question: "Moet een school toestemming vragen voor foto's van leerlingen op de website volgens EU-regels?", expectGap: false },
  { id: "V18", question: "Ik importeer een klassieke auto uit Italië. Welke EU-emissie-eisen gelden bij registratie?", expectGap: false },
];

function scoreCase(testCase, data) {
  if (testCase.expectGap) {
    return ["insufficient", "irrelevant"].includes(data.coverage_status) ? "GOED" : "SLECHT";
  }
  return isHeldereUitgelegd(data) ? "GOED" : "SLECHT";
}

async function query(question) {
  return auditQuery(BASE, question);
}

async function main() {
  const results = [];
  let good = 0;
  if (!jsonOut) {
    console.log(`Fresh layperson audit → ${BASE}`);
    console.log(`Gate: ≥${GOED_THRESHOLD}/18 GOED (strict)\n`);
  }
  for (let i = 0; i < CASES.length; i += 1) {
    const tc = CASES[i];
    if (i > 0) await sleep(DELAY_MS);
    if (!jsonOut) process.stdout.write(`${tc.id} … `);
    try {
      const data = await query(tc.question);
      const clarity = scoreCase(tc, data);
      if (!jsonOut) console.log(clarity);
      if (clarity === "GOED") good += 1;
      else if (!jsonOut) {
        console.log(`       cov=${data.coverage_status} route=${data.retrieval_route || "-"}`);
        console.log(`       → ${(data.answer || "").slice(0, 160).replace(/\n/g, " ")}…`);
      }
      results.push({ ...tc, clarity, coverage: data.coverage_status });
    } catch (err) {
      if (!jsonOut) console.log("ERROR");
      results.push({ ...tc, clarity: "ERROR", error: err.message });
    }
  }
  if (jsonOut) {
    console.log(JSON.stringify({ set: "V", good, total: CASES.length, threshold: GOED_THRESHOLD, results }, null, 2));
  } else {
    console.log(`\nGOED: ${good}/${CASES.length} (drempel ${GOED_THRESHOLD})`);
  }
  if (good < GOED_THRESHOLD) process.exit(1);
}

main();

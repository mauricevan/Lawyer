#!/usr/bin/env node
/**
 * Novel layperson audit — unseen questions, strict scoring.
 * Usage: node scripts/qa/layperson-novel-audit.mjs [baseUrl] [--json]
 * Exit 1 when GOED < 18/18 (strict)
 */
import { isHeldereUitgelegd, parseAuditArgs } from "./layperson-audit-lib.mjs";
import { auditQuery, sleep } from "./audit-fetch.mjs";

const { base: BASE, jsonOut } = parseAuditArgs(process.argv);
const GOED_THRESHOLD = 18;
const DELAY_MS = 3500;

const CASES = [
  { id: "N01", question: "Mijn kind is 15. Mag TikTok zijn gegevens bewaren volgens EU-regels?", expectGap: false },
  { id: "N02", question: "Ik huur een huis in Spanje. Welke EU-regels beschermen mij als huurder?", expectGap: false },
  { id: "N03", question: "De supermarkt weigert contant geld te accepteren. Mag dat in de EU?", expectGap: false },
  { id: "N04", question: "Ik werk in Nederland maar woon in Duitsland. Welke EU-regels gelden voor mijn sociale zekerheid?", expectGap: false },
  { id: "N05", question: "Een app vraagt toegang tot mijn contacten. Moet ik daarmee instemmen volgens de AVG?", expectGap: false },
  { id: "N06", question: "Ik bestelde eten via Deliveroo en werd ziek. Kan ik de verkoper aansprakelijk stellen volgens EU-recht?", expectGap: false },
  { id: "N07", question: "Mijn telefoonabonnement loopt 3 jaar. Mag de provider me vastzetten volgens EU-regels?", expectGap: false },
  { id: "N08", question: "Ik start een webshop en verkoop aan consumenten in Frankrijk. Welke EU-regels moet ik kennen?", expectGap: false },
  { id: "N09", question: "Mag de politie mijn telefoon uitlezen zonder warrant onder EU-regels?", expectGap: false },
  { id: "N10", question: "Ik ben zwanger en mijn baas wil me ontslaan. Beschermt EU-recht mij?", expectGap: false },
  { id: "N11", question: "Hoe lang mag een EU-bedrijf mijn sollicitatiegegevens bewaren?", expectGap: false },
  { id: "N12", question: "Ik koop een tweedehands auto met verborgen gebreken uit België. Helpt EU-recht mij?", expectGap: false },
  { id: "N13", question: "Mag ik met mijn Nederlandse rijbewijs in Italië rijden volgens EU-regels?", expectGap: false },
  { id: "N14", question: "Onze vereniging verwerkt ledenlijsten. Moeten we ons registreren bij de AP volgens EU-recht?", expectGap: false },
  { id: "N15", question: "Wat is het maximum aantal uur dat ik per week mag werken volgens EU-regels?", expectGap: false },
  { id: "N16", question: "Hoeveel parkeerboetes mag ik in België krijgen volgens Belgisch recht?", expectGap: true },
  { id: "N17", question: "Ik importeer wijn uit Frankrijk voor eigen gebruik. Hoeveel liter mag dat volgens EU-douane?", expectGap: false },
  { id: "N18", question: "Mijn slimme thermostaat verzamelt data. Welke EU-regels gelden daarvoor?", expectGap: false },
];

function scoreCase(testCase, data) {
  if (testCase.expectGap) {
    return ["insufficient", "irrelevant"].includes(data.coverage_status) ? "GOED" : "SLECHT";
  }
  return isHeldereUitgelegd(data) ? "GOED" : "SLECHT";
}

async function main() {
  const results = [];
  let good = 0;
  if (!jsonOut) {
    console.log(`Novel layperson audit → ${BASE}`);
    console.log(`Gate: ≥${GOED_THRESHOLD}/18 GOED (strict)\n`);
  }
  for (let i = 0; i < CASES.length; i += 1) {
    const tc = CASES[i];
    if (i > 0) await sleep(DELAY_MS);
    if (!jsonOut) process.stdout.write(`${tc.id} … `);
    try {
      const data = await auditQuery(BASE, tc.question);
      const clarity = scoreCase(tc, data);
      if (!jsonOut) {
        console.log(clarity);
        if (clarity !== "GOED") {
          console.log(`       cov=${data.coverage_status} route=${data.retrieval_route || "-"}`);
          console.log(`       → ${(data.answer || "").slice(0, 160).replace(/\n/g, " ")}…`);
        }
      }
      if (clarity === "GOED") good += 1;
      results.push({ ...tc, clarity, coverage: data.coverage_status, route: data.retrieval_route });
    } catch (err) {
      if (!jsonOut) console.log("ERROR");
      results.push({ ...tc, clarity: "ERROR", error: err.message });
    }
  }
  if (jsonOut) {
    console.log(JSON.stringify({ set: "N", good, total: CASES.length, threshold: GOED_THRESHOLD, results }, null, 2));
  } else {
    console.log(`\nGOED: ${good}/${CASES.length} (drempel ${GOED_THRESHOLD})`);
  }
  if (good < GOED_THRESHOLD) process.exit(1);
}

main();

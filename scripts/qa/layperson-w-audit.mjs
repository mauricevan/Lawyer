#!/usr/bin/env node
/**
 * W-set layperson audit — new topics + expected gaps.
 * Usage: node scripts/qa/layperson-w-audit.mjs [baseUrl] [--json]
 */
import { isHeldereUitgelegd, parseAuditArgs, scoreAuditCase } from "./layperson-audit-lib.mjs";
import { auditQuery, sleep } from "./audit-fetch.mjs";

const { base: BASE, jsonOut } = parseAuditArgs(process.argv);
const CASES = [
  { id: "W01", question: "ik krijg spam sms wat zijn mijn rechten", expected_route: "layperson_topic", must_mention: ["sms", "ePrivacy", "opt-in"] },
  { id: "W02", question: "mijn nft is waardeloos na oplichting", expected_route: "layperson_topic", must_mention: ["mica", "oplichting"] },
  { id: "W03", question: "mag mijn partner mijn auto volgen met gps tracker", expected_route: "layperson_topic", must_mention: ["avg", "gps"] },
  { id: "W04", question: "foodtruck hygiëne regels op markt", expected_route: "layperson_topic", must_mention: ["voedsel", "hygi"] },
  { id: "W05", question: "pensioen opbouwen werken in duitsland", expected_route: "layperson_topic", must_mention: ["pensioen"] },
  { id: "W06", question: "maaltijdbox abonnement ineens duurder", expected_route: "layperson_topic", must_mention: ["abonnement", "consument"] },
  { id: "W07", question: "bezorgdrone registratie voor pakketten", expected_route: "layperson_topic", must_mention: ["drone", "registr"] },
  { id: "W08", question: "vereniging ledenlijst avg verwerking", expected_route: "layperson_topic", must_mention: ["avg", "vereniging"] },
  { id: "W09", question: "gekochte game download werkt niet", expected_route: "layperson_topic", must_mention: ["digitaal", "gebrek"] },
  { id: "W10", question: "instapweigering vlucht overboeking", expected_route: "layperson_topic", must_mention: ["compensatie", "passagier"] },
  { id: "W11", question: "webshop dark pattern moeilijk opzeggen", expected_route: "layperson_topic", must_mention: ["misleid", "consument"] },
  { id: "W12", question: "co2 norm nieuwe auto kopen 2024", expected_route: "layperson_topic", must_mention: ["co2", "auto"] },
  { id: "W13", question: "ai beslissing sollicitatie afgewezen", expected_route: "layperson_topic", must_mention: ["ai"] },
  { id: "W14", question: "pakket verloren uit duitsland webshop", expected_route: "layperson_topic", must_mention: ["pakket"] },
  { id: "W15", question: "app vraagt contacten toestemming avg", expected_route: "layperson_topic", must_mention: ["contacten", "avg"] },
  { id: "W16", question: "webshop starten verkopen frankrijk consumenten", expected_route: "layperson_topic", must_mention: ["consument"] },
  { id: "W17", question: "telefoonabonnement 3 jaar vast contract", expected_route: "layperson_topic", must_mention: ["abonnement"] },
  { id: "W18", question: "vervoerder aansprakelijk beschadigde vracht", expected_route: "layperson_topic", must_mention: ["vervoerder", "aansprakelijk"] },
  { id: "W19", question: "abonnement automatisch verlengd zonder mail", expected_route: "layperson_topic", must_mention: ["abonnement"] },
  { id: "W20", question: "nepreviews op marketplace webshop", expected_route: "layperson_topic", must_mention: ["review", "dsa"] },
  { id: "W21", expectGap: true, question: "wat is het minimumloon in nederland" },
  { id: "W22", expectGap: true, question: "parkeerboete belgie bezwaar maken" },
  { id: "W23", expectGap: true, question: "hoeveel jaar celstraf belastingfraude belgie" },
  { id: "W24", expectGap: true, question: "hoeveel vakantiedagen volgens nederlandse wet" },
  { id: "W25", expectGap: true, question: "nederlandse parkeerregels amsterdam" },
  { id: "W26", expectGap: true, question: "gemeentelijke afvalstoffenheffing hoogte" },
  { id: "W27", expectGap: true, question: "standplaatsvergunning markt nederland" },
  { id: "W28", expectGap: true, question: "notaris kosten erfenis alleen nederland" },
  { id: "W29", expectGap: true, question: "studiefinanciering duos regels nederland" },
  { id: "W30", expectGap: true, question: "waterschapsbelasting nederland hoogte" },
];

const GOED_THRESHOLD = Math.ceil(CASES.length * 0.7);
const DELAY_MS = 3500;

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
    console.log(`W-set layperson audit → ${BASE}`);
    console.log(`Gate: ≥${GOED_THRESHOLD}/${CASES.length} GOED (70%)\n`);
  }
  for (let i = 0; i < CASES.length; i += 1) {
    const tc = CASES[i];
    if (i > 0) await sleep(DELAY_MS);
    if (!jsonOut) process.stdout.write(`${tc.id} … `);
    try {
      const data = await auditQuery(BASE, tc.question);
      const scored = scoreAuditCase(tc, data, scoreCase);
      if (!jsonOut) {
        console.log(scored.clarity);
        if (scored.clarity !== "GOED") {
          console.log(`       cov=${data.coverage_status} route=${data.retrieval_route || "-"}`);
          if (scored.semanticIssues?.length) console.log(`       ⚠ ${scored.semanticIssues.join("; ")}`);
        }
      }
      if (scored.clarity === "GOED") good += 1;
      results.push({ ...tc, ...scored, coverage: data.coverage_status, route: data.retrieval_route });
    } catch (err) {
      if (!jsonOut) console.log("ERROR");
      results.push({ ...tc, clarity: "ERROR", error: err.message });
    }
  }
  const summary = { set: "W", good, total: CASES.length, threshold: GOED_THRESHOLD, results };
  if (jsonOut) {
    console.log(JSON.stringify(summary, null, 2));
  } else {
    console.log(`\nGOED: ${good}/${CASES.length} (drempel ${GOED_THRESHOLD})`);
  }
  if (good < GOED_THRESHOLD) process.exit(1);
}

main();

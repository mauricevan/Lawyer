/**
 * Live headed browser demo — layperson with a custom tricky question.
 * Keeps the window open so the user can watch and explore.
 */
import { chromium } from "playwright";

const BASE = "http://localhost:3000";
const TRICKY_QUESTION =
  "Mijn werkgever wil mijn e-mails en Teams-chats door een AI laten scannen om te meten of ik productief genoeg ben. Mag dat zonder dat ik daar expliciet mee instem, en wat kan ik doen als ik het oneerlijk vind?";

async function pause(page, ms = 2500) {
  await page.waitForTimeout(ms);
}

async function main() {
  const browser = await chromium.launch({
    headless: false,
    slowMo: 600,
    args: ["--start-maximized"],
  });

  const context = await browser.newContext({ viewport: null });
  const page = await context.newPage();

  console.log("\n=== LIVE LEEK-DEMO — kijk mee in het Chrome-venster ===\n");

  await page.goto(BASE, { waitUntil: "networkidle" });
  console.log("Stap 1: Landingspagina — Begrijpelijke uitleg staat al aan.");
  await pause(page, 3000);

  await page.getByText("Geldt dit voor mijn situatie?", { exact: false }).click();
  console.log("Stap 2: Modus gekozen — Geldt dit voor mijn situatie?");
  await pause(page, 2500);

  const input = page.locator("#chat-input");
  await input.click();
  await input.fill("");
  await input.pressSequentially(TRICKY_QUESTION, { delay: 25 });
  console.log("Stap 3: Lastige eigen vraag getypt (niet op de homepage).");
  await pause(page, 3500);

  await page.getByRole("button", { name: "Stel vraag" }).click();
  console.log("Stap 4: Vraag verstuurd — wacht op antwoord (~20-60 sec)...");
  await page.waitForSelector("text=Bezig met antwoorden", { timeout: 20000 });

  await page.waitForFunction(
    () => {
      const body = document.body.innerText;
      if (body.includes("Failed to fetch")) return false;
      const loading = body.includes("Bezig met antwoorden");
      const coverageGap =
        body.includes("buiten wat ik nu betrouwbaar") ||
        body.includes("Waar u verder kunt terecht");
      const hasMisschien = /\bmisschien\b/i.test(body);
      return !loading && coverageGap && !hasMisschien;
    },
    { timeout: 120000 },
  );

  console.log("Stap 5: Antwoord binnen — bronnen uitklappen...");
  await pause(page, 2000);

  const sourcesBtn = page.getByRole("button", { name: /Bekijk de verordeningen/i });
  if (await sourcesBtn.isVisible().catch(() => false)) {
    await sourcesBtn.click();
    await pause(page, 2000);
  }

  console.log("\nDemo klaar. Browser blijft 10 minuten open — scroll en stel gerust een vervolgvraag.\n");
  await pause(page, 600_000);
  await browser.close();
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});

/**
 * Layperson customer journey demo — captures screenshots for walkthrough.
 */
import { chromium } from "playwright";
import { mkdir } from "node:fs/promises";
import path from "node:path";

const BASE = "http://localhost:3000";
const OUT = "/home/mau/Desktop/Projecs/Lawyer/docs/demo/layperson-journey";

async function expectEnabled(locator) {
  await locator.waitFor({ state: "visible" });
  for (let i = 0; i < 20; i++) {
    if (await locator.isEnabled()) return;
    await locator.page().waitForTimeout(100);
  }
}

async function shot(page, name) {
  await page.screenshot({ path: path.join(OUT, `${name}.png`), fullPage: true });
}

async function main() {
  await mkdir(OUT, { recursive: true });
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage({ viewport: { width: 1280, height: 900 } });
  page.on("requestfailed", (req) => {
    if (req.url().includes("/query")) {
      console.error("Request failed:", req.url(), req.failure()?.errorText);
    }
  });

  // Step 1: Land on homepage
  await page.goto(BASE, { waitUntil: "networkidle" });
  await shot(page, "01-landing");

  // Step 2: Ensure layperson mode (default) — click compliance mode
  await page.getByText("Geldt dit voor mijn situatie?", { exact: false }).click();
  await shot(page, "02-kies-situatie");

  // Step 3: Click example question (compliance mode)
  await page.getByRole("button", {
    name: "Moet ik mijn chatbot registreren bij de overheid?",
  }).first().click();
  await page.waitForTimeout(300);
  await shot(page, "03-vraag-ingevuld");

  // Step 4: Submit — wait until button is enabled
  const submitBtn = page.getByRole("button", { name: "Stel vraag" });
  await submitBtn.waitFor({ state: "visible" });
  await expectEnabled(submitBtn);
  await submitBtn.click();

  // Step 5: Chat view — wait for real assistant answer (not just user bubble)
  await page.waitForSelector("text=Bezig met antwoorden", { timeout: 20000 });

  await page.waitForFunction(
    () => {
      const body = document.body.innerText;
      if (body.includes("Failed to fetch")) return false;
      const hasLoading = body.includes("Bezig met antwoorden");
      const hasSources =
        body.includes("Bronnen en verwijzingen") ||
        body.includes("Gebruikte bronnen");
      const hasSubstantiveAnswer = body.includes("AI Act") || body.includes("registr");
      return !hasLoading && (hasSources || hasSubstantiveAnswer);
    },
    { timeout: 120000 },
  );

  await page.waitForTimeout(1000);

  await shot(page, "04-antwoord-met-bronnen");

  // Step 6: Expand citations for layperson trust moment
  const sourcesBtn = page.getByRole("button", { name: /Bekijk de verordeningen/i });
  if (await sourcesBtn.isVisible().catch(() => false)) {
    await sourcesBtn.click();
    await page.waitForTimeout(500);
  }
  await shot(page, "05-bronnen-detail");

  console.log(`Screenshots saved to ${OUT}`);
  await browser.close();
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});

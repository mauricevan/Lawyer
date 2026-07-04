/**
 * Layperson customer journey demo — captures screenshots for walkthrough.
 */
import { chromium } from "playwright";
import { mkdir } from "node:fs/promises";
import path from "node:path";

const BASE = "http://127.0.0.1:3000";
const OUT = path.resolve("docs/demo/layperson-journey");

async function shot(page, name) {
  await page.screenshot({ path: path.join(OUT, `${name}.png`), fullPage: true });
}

async function main() {
  await mkdir(OUT, { recursive: true });
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage({ viewport: { width: 1280, height: 900 } });

  // Step 1: Land on homepage
  await page.goto(BASE, { waitUntil: "networkidle" });
  await shot(page, "01-landing");

  // Step 2: Ensure layperson mode (default) — click compliance mode
  await page.getByText("Geldt dit voor mijn situatie?", { exact: false }).click();
  await shot(page, "02-kies-situatie");

  // Step 3: Click example question (compliance mode)
  await page.getByRole("button", {
    name: "Moet ik mijn chatbot registreren bij de overheid?",
  }).click();
  await shot(page, "03-vraag-ingevuld");

  // Step 4: Submit
  await page.getByRole("button", { name: "Stel vraag" }).click();

  // Step 5: Wait for answer (up to 90s)
  await page.waitForSelector("text=Juridisch assistent", { timeout: 10000 });

  await page.waitForFunction(
    () => {
      const body = document.body.innerText;
      const hasAnswer = body.includes("EUR-Lex") || body.includes("AI Act") || body.length > 1200;
      const stillLoading = body.includes("Zoeken") && !hasAnswer;
      return hasAnswer && !stillLoading;
    },
    { timeout: 90000 },
  ).catch(async () => {
    await page.waitForTimeout(20000);
  });

  await shot(page, "04-antwoord-met-bronnen");

  // Step 6: Scroll to citations if present
  await page.evaluate(() => window.scrollTo(0, document.body.scrollHeight / 2));
  await page.waitForTimeout(500);
  await shot(page, "05-bronnen-detail");

  console.log(`Screenshots saved to ${OUT}`);
  await browser.close();
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});

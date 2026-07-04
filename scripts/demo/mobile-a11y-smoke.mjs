/**
 * Mobile accessibility smoke — 320px viewport, no horizontal overflow.
 */
import { chromium } from "playwright";

const BASE = process.env.BASE_URL || "http://localhost:3000";

async function main() {
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage({ viewport: { width: 320, height: 568 } });
  await page.goto(BASE, { waitUntil: "networkidle" });

  const scrollWidth = await page.evaluate(() => document.documentElement.scrollWidth);
  const clientWidth = await page.evaluate(() => document.documentElement.clientWidth);
  if (scrollWidth > clientWidth + 2) {
    throw new Error(`Horizontal overflow: scrollWidth=${scrollWidth} clientWidth=${clientWidth}`);
  }

  const buttons = page.locator("button, a[href], input[type='submit']");
  const count = await buttons.count();
  for (let i = 0; i < Math.min(count, 8); i++) {
    const box = await buttons.nth(i).boundingBox();
    if (box && box.height < 40) {
      console.warn(`Small tap target at index ${i}: height=${box.height}`);
    }
  }

  await browser.close();
  console.log("Mobile a11y smoke: OK (320px, no overflow)");
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});

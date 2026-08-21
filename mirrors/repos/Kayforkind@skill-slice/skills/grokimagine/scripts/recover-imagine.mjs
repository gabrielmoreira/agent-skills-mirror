import { chromium } from "playwright-core";

const browser = await chromium.connectOverCDP(
  process.env.GROK_CDP || "http://127.0.0.1:9222",
);
const ctx = browser.contexts()[0];
let page =
  ctx.pages().find((p) => /grok\.com/i.test(p.url())) || ctx.pages()[0];
if (!page) page = await ctx.newPage();

await page.goto("https://grok.com/imagine", {
  waitUntil: "domcontentloaded",
  timeout: 90000,
});
await page.waitForTimeout(4500);
const ng = page.locator('[aria-label="New Generation"]');
if (await ng.count()) {
  await ng.first().click({ force: true }).catch(() => {});
  await page.waitForTimeout(1500);
}
await page
  .locator('[role="radio"][aria-label="Video"]')
  .first()
  .click({ force: true })
  .catch(() => {});
await page.waitForTimeout(800);
const ask = await page.getByRole("textbox", { name: /ask grok/i }).count();
const out = (process.env.GROK_OUT || "").trim();
if (!out) {
  console.error("Set GROK_OUT to a local directory. This script has no machine default.");
  process.exit(2);
}
await page.screenshot({ path: `${out}\\recover.png`, fullPage: false }).catch(() => null);
console.log(
  JSON.stringify({
    ok: ask > 0,
    url: page.url(),
    title: await page.title(),
    askBoxes: ask,
  }),
);
process.exit(ask > 0 ? 0 : 2);

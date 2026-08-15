/**
 * Grok Imagine Image stills (clean New Generation, 16:9 Quality).
 * Real Chrome CDP only. Requires GROK_OUT and GROK_PROMPT or GROK_PROMPT_FILE.
 */
import { chromium } from "playwright-core";
import fs from "fs";
import path from "path";
import {
  ensureOneImagineTab,
  goCleanImagineHome,
  selectGenerationMode,
  setAspect169,
  setImageQuality,
  submitImagine,
} from "./ui-mode.mjs";

function requireEnv(name) {
  const v = (process.env[name] || "").trim();
  if (!v) {
    console.error(`Set ${name} to a local path. This script has no machine default.`);
    process.exit(2);
  }
  return v;
}

const CDP = process.env.GROK_CDP || "http://127.0.0.1:9222";
const OUT = requireEnv("GROK_OUT");
const PROMPT =
  (process.env.GROK_PROMPT || "").trim() ||
  fs.readFileSync(requireEnv("GROK_PROMPT_FILE"), "utf8");
const WANT = Number(process.env.GROK_COUNT || "2");
const WAIT_MS = Number(process.env.GROK_WAIT_MS || "240000");

fs.mkdirSync(OUT, { recursive: true });
const stamp = () => new Date().toISOString().replace(/[:.]/g, "-");

async function snap(page, label) {
  const f = path.join(OUT, `${stamp()}_${label}.png`);
  await page.screenshot({ path: f, fullPage: false }).catch(() => null);
  return f;
}

async function getPage(browser) {
  const ctx = browser.contexts()[0] || (await browser.newContext());
  let page =
    ctx.pages().find((p) => /grok\.com/i.test(p.url())) || ctx.pages()[0];
  if (!page) page = await ctx.newPage();
  return page;
}

async function newGeneration(page) {
  // Prefer sidebar New Generation
  const ng = page.getByText(/^New Generation$/i);
  if (await ng.count()) {
    await ng.first().click({ force: true }).catch(() => {});
    await page.waitForTimeout(1500);
  } else {
    await page.keyboard.press("Control+J").catch(() => {});
    await page.waitForTimeout(1500);
  }
  const np = page.getByRole("button", { name: /new project/i });
  if (await np.count()) {
    await np.first().click({ force: true }).catch(() => {});
    await page.waitForTimeout(1200);
  }
  // Leave agent URLs
  if (/\/imagine\/agent/i.test(page.url())) {
    await page.goto("https://grok.com/imagine", {
      waitUntil: "domcontentloaded",
      timeout: 60000,
    });
    await page.waitForTimeout(2000);
  }
}

async function setQuality169(page) {
  await setImageQuality(page);
  await setAspect169(page);
}

async function forceImageNotVideo(page) {
  // Default landing is often Video. Unselected Image radio has EMPTY visible text —
  // must click [role=radio][aria-label=Image], never button:has-text("Image").
  return selectGenerationMode(page, "Image");
}

async function typePrompt(page, text) {
  const box = page
    .locator(
      '[role="textbox"][aria-label*="imagine" i], [role="textbox"][aria-label*="Ask" i], .tiptap.ProseMirror, [contenteditable="true"], textarea',
    )
    .last();
  if (!(await box.count())) return false;
  await box.click({ force: true });
  await page.keyboard.press("Control+A");
  await page.keyboard.press("Backspace");
  await page.keyboard.type(text.trim(), { delay: 5 });
  await page.waitForTimeout(400);
  return true;
}

async function submit(page) {
  return submitImagine(page);
}

async function collect(page) {
  return page.evaluate(() => {
    const out = [];
    for (const img of document.querySelectorAll("img")) {
      const src = img.currentSrc || img.src || "";
      if (!src) continue;
      const nw = img.naturalWidth || 0;
      const nh = img.naturalHeight || 0;
      const r = img.getBoundingClientRect();
      const alt = img.alt || "";
      const isGen = /generated/i.test(alt);
      if (nw < 512 || nh < 512) continue;
      if (!(isGen || (r.width >= 180 && r.height >= 180))) continue;
      if (/avatar|icon|logo|emoji/i.test(src) && nw < 600) continue;
      out.push({
        src: src.slice(0, 800),
        full: src.startsWith("data:") ? src : src,
        nw,
        nh,
        w: Math.round(r.width),
        h: Math.round(r.height),
        alt,
        isGen,
      });
    }
    out.sort((a, b) => (b.isGen - a.isGen) || b.nw * b.nh - a.nw * a.nh);
    return out;
  });
}

function key(a) {
  const s = a.full || a.src || "";
  if (s.startsWith("data:"))
    return `data:${a.nw}x${a.nh}:${s.length}:${s.slice(0, 48)}:${s.slice(-24)}`;
  return s.split("?")[0];
}

async function download(page, asset, i) {
  const file = path.join(OUT, `maya_hero_${String(i).padStart(2, "0")}_${stamp()}.png`);
  const src = asset.full || asset.src;
  if (src.startsWith("data:")) {
    fs.writeFileSync(file, Buffer.from(src.split(",")[1], "base64"));
    return file;
  }
  if (src.startsWith("blob:")) {
    const buf = await page.evaluate(async (s) => {
      const res = await fetch(s);
      const ab = await res.arrayBuffer();
      return Array.from(new Uint8Array(ab));
    }, src);
    fs.writeFileSync(file, Buffer.from(buf));
    return file;
  }
  const res = await page.request.get(src);
  if (!res.ok()) throw new Error(`HTTP ${res.status()}`);
  fs.writeFileSync(file, await res.body());
  return file;
}

const browser = await chromium.connectOverCDP(CDP);
const ctx = browser.contexts()[0] || (await browser.newContext());
let page = await ensureOneImagineTab(ctx);
if (!page) page = await getPage(browser);

await goCleanImagineHome(page);
await newGeneration(page);
const mode = await forceImageNotVideo(page);
if (!mode.ok) {
  console.log(JSON.stringify({ ok: false, reason: "image_mode_failed", mode }, null, 2));
  process.exit(6);
}
await setQuality169(page);

const before = await collect(page);
const beforeKeys = new Set(before.map(key));
const beforeShot = await snap(page, "clean_before");

const typed = await typePrompt(page, PROMPT);
if (!typed) {
  console.log(JSON.stringify({ ok: false, reason: "no_composer", beforeShot }, null, 2));
  process.exit(3);
}

const submitHow = await submit(page);
await page.waitForTimeout(5000);

const start = Date.now();
let fresh = [];
while (Date.now() - start < WAIT_MS) {
  if (/\/imagine\/agent/i.test(page.url())) {
    // Wrong surface — bail and report
    const afterShot = await snap(page, "unexpected_agent");
    console.log(
      JSON.stringify(
        {
          ok: false,
          reason: "redirected_to_agent",
          url: page.url(),
          afterShot,
          submitHow,
        },
        null,
        2,
      ),
    );
    process.exit(5);
  }
  const now = await collect(page);
  fresh = now.filter((a) => !beforeKeys.has(key(a)));
  if (fresh.length >= 1) break;
  await page.waitForTimeout(2500);
}

const afterShot = await snap(page, "clean_after");
if (!fresh.length) {
  console.log(
    JSON.stringify(
      { ok: false, reason: "timeout", beforeShot, afterShot, url: page.url(), submitHow },
      null,
      2,
    ),
  );
  process.exit(4);
}

const saved = [];
for (let i = 0; i < Math.min(WANT, fresh.length); i++) {
  saved.push(await download(page, fresh[i], i + 1));
}

console.log(
  JSON.stringify(
    {
      ok: true,
      saved,
      dims: fresh.slice(0, WANT).map((a) => `${a.nw}x${a.nh}`),
      beforeShot,
      afterShot,
      url: page.url(),
      submitHow,
    },
    null,
    2,
  ),
);
process.exit(0);

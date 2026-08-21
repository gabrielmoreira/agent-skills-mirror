/**
 * Grok Imagine text→video (no still). Real Chrome CDP.
 * Usage:
 *   $env:GROK_OUT=...
 *   $env:GROK_PROMPT=...
 *   $env:GROK_ID=F01
 *   node t2v-one.mjs
 */
import { chromium } from "playwright-core";
import fs from "fs";
import path from "path";

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
const PROMPT = process.env.GROK_PROMPT || "";
const ID = process.env.GROK_ID || "clip";
const WAIT_MS = Number(process.env.GROK_WAIT_MS || "300000");

fs.mkdirSync(OUT, { recursive: true });
const stamp = () => new Date().toISOString().replace(/[:.]/g, "-");

async function getPage(browser) {
  const ctx = browser.contexts()[0] || (await browser.newContext());
  // ONE tab only: reuse existing clean /imagine (never Agent Mode, never newPage spam)
  let page = ctx
    .pages()
    .find(
      (p) =>
        /grok\.com\/imagine\/?(\?|$|#)/i.test(p.url()) &&
        !/\/imagine\/agent/i.test(p.url()),
    );
  if (!page) {
    // Prefer any grok.com page that isn't agent, else first page — navigate in place
    page =
      ctx.pages().find((p) => /grok\.com/i.test(p.url()) && !/agent/i.test(p.url())) ||
      ctx.pages()[0];
    if (!page) {
      throw new Error(
        "No Chrome page in owned hub. Open https://grok.com/imagine once in the CDP Chrome window.",
      );
    }
    await page.goto("https://grok.com/imagine", {
      waitUntil: "domcontentloaded",
      timeout: 60000,
    });
  }
  await page.bringToFront().catch(() => {});
  // Leave Agent tabs alone — do not open extras
  for (let i = 0; i < 15; i++) {
    const n = await page
      .locator(
        '[contenteditable="true"], textarea, [role="textbox"][aria-label*="imagine" i], [role="textbox"][aria-label*="Ask" i], .tiptap.ProseMirror',
      )
      .count();
    if (n > 0) break;
    await page.waitForTimeout(800);
  }
  return page;
}

async function forceVideo(page) {
  const radio = page.getByRole("radio", { name: /^Video$/i });
  if (await radio.count()) {
    await radio.first().click({ force: true }).catch(() => {});
    await page.waitForTimeout(500);
    return;
  }
  const btn = page.getByRole("button", { name: /^Video$/i });
  if (await btn.count()) await btn.first().click({ force: true }).catch(() => {});
  // camera icon near composer
  const cam = page.locator('button[aria-label*="Video" i]');
  if (await cam.count()) await cam.first().click({ force: true }).catch(() => {});
}

async function newGen(page) {
  const ng = page.getByText(/^New Generation$/i);
  if (await ng.count()) {
    await ng.first().click({ force: true }).catch(() => {});
    await page.waitForTimeout(1200);
  }
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
  const send = page.locator('button[aria-label="Send"], button[aria-label="Submit"]');
  if (await send.count()) {
    const b = send.last();
    if (!(await b.isDisabled().catch(() => false))) {
      await b.click();
      return "send";
    }
  }
  await page.keyboard.press("Enter");
  return "enter";
}

async function collect(page) {
  return page.evaluate(() => {
    const out = [];
    for (const v of document.querySelectorAll("video")) {
      const src = v.currentSrc || v.src || "";
      if (!src) continue;
      const r = v.getBoundingClientRect();
      const uuid = (src.match(/generated\/([a-f0-9-]{20,})/i) || [])[1] || null;
      out.push({
        src,
        uuid,
        hosted: /assets\.grok\.com|imagine-public\.x\.ai/i.test(src),
        w: Math.round(r.width),
        h: Math.round(r.height),
        vw: v.videoWidth || 0,
        vh: v.videoHeight || 0,
      });
    }
    for (const a of document.querySelectorAll("a[href]")) {
      const href = a.href || "";
      if (/generated_video\.mp4/i.test(href)) {
        const uuid = (href.match(/generated\/([a-f0-9-]{20,})/i) || [])[1] || null;
        out.push({ src: href, uuid, hosted: true, w: 0, h: 0, vw: 0, vh: 0 });
      }
    }
    out.sort((a, b) => b.w * b.h - a.w * a.h);
    return out;
  });
}

async function download(page, video) {
  const short = (video.uuid || ID || "vid").slice(0, 12);
  const outFile = path.join(OUT, `${ID}_${short}_${stamp()}.mp4`);
  const src = video.src;
  if (src.startsWith("blob:")) {
    const buf = await page.evaluate(async (s) => {
      const res = await fetch(s);
      const ab = await res.arrayBuffer();
      return Array.from(new Uint8Array(ab));
    }, src);
    fs.writeFileSync(outFile, Buffer.from(buf));
    return outFile;
  }
  const res = await page.request.get(src);
  if (!res.ok()) throw new Error(`HTTP ${res.status()}`);
  fs.writeFileSync(outFile, await res.body());
  return outFile;
}

if (!PROMPT.trim()) {
  console.log(JSON.stringify({ ok: false, reason: "empty_prompt" }));
  process.exit(2);
}

const browser = await chromium.connectOverCDP(CDP);
const page = await getPage(browser);
await page.goto("https://grok.com/imagine", {
  waitUntil: "domcontentloaded",
  timeout: 60000,
});
await page.waitForTimeout(2000);
await newGen(page);
await forceVideo(page);

const before = await collect(page);
const beforeSrcs = new Set(before.map((v) => v.src));

const typed = await typePrompt(page, PROMPT);
if (!typed) {
  console.log(JSON.stringify({ ok: false, reason: "no_composer" }));
  process.exit(3);
}
const how = await submit(page);
await page.waitForTimeout(8000);

const start = Date.now();
let fresh = [];
while (Date.now() - start < WAIT_MS) {
  const now = await collect(page);
  fresh = now.filter((v) => v.hosted && !beforeSrcs.has(v.src));
  if (fresh.length) break;
  await page.waitForTimeout(3000);
}

if (!fresh.length) {
  await page.screenshot({
    path: path.join(OUT, `${ID}_timeout_${stamp()}.png`),
    fullPage: false,
  });
  console.log(JSON.stringify({ ok: false, reason: "timeout", how, id: ID }));
  process.exit(5);
}

fresh.sort((a, b) => b.w * b.h - a.w * a.h);
const saved = [];
// download up to 2 unique hosted videos from this gen
for (const v of fresh.slice(0, 2)) {
  try {
    const f = await download(page, v);
    if (fs.statSync(f).size > 80_000) saved.push(f);
  } catch (e) {
    /* continue */
  }
}

console.log(
  JSON.stringify(
    {
      ok: saved.length > 0,
      id: ID,
      how,
      saved,
      freshCount: fresh.length,
    },
    null,
    2,
  ),
);
process.exit(saved.length ? 0 : 4);

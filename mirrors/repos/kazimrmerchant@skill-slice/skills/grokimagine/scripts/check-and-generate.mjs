/**
 * Grok Imagine helper — real Chrome via CDP only.
 * Modes: status | generate (default Image path) | generate-agent
 *
 * Research (2026):
 * - Single still: Image mode → prompt → Send/Generate (NOT Agent)
 * - Multi-step: Agent mode → free-form brief or presets → infinite canvas nodes
 * - Assets host: assets.grok.com/users/.../generated/...
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


const CDP = process.env.GROK_CDP || "http://127.0.0.1:9222";
const OUT = process.env.GROK_OUT || "C:\\Users\\user\\.cursor\\grok-chrome\\out";
const PROMPT =
  process.env.GROK_PROMPT ||
  "Simple test render: a single glossy blue marble on a clean white studio surface, soft shadow, high detail, photoreal";
const MODE = process.argv[2] || "status";
const WANT_COUNT = Number(process.env.GROK_COUNT || "1");

fs.mkdirSync(OUT, { recursive: true });

function stamp() {
  return new Date().toISOString().replace(/[:.]/g, "-");
}

async function getPage(browser) {
  const context = browser.contexts()[0] || (await browser.newContext());
  let page = await ensureOneImagineTab(context);
  if (!page) {
    page =
      context.pages().find((p) => /grok\.com|accounts\.x\.ai/i.test(p.url())) ||
      context.pages()[0];
  }
  // Only create a tab if hub has zero pages — never spray extras
  if (!page) page = await context.newPage();
  return page;
}

async function snapshot(page, label) {
  const file = path.join(OUT, `${stamp()}_${label}.png`);
  try {
    await page.screenshot({ path: file, fullPage: false, timeout: 15000 });
    return file;
  } catch (e) {
    console.error("snapshot_soft_fail", label, String(e).slice(0, 120));
    return null;
  }
}

async function pageInfo(page) {
  const url = page.url();
  const title = await page.title();
  const signedOut = await page
    .locator('button:has-text("Sign in"), a:has-text("Sign in")')
    .count()
    .catch(() => 0);
  const hasComposer = await page
    .locator('[role="textbox"], textarea, [contenteditable="true"]')
    .count()
    .catch(() => 0);
  const bodyText = await page.locator("body").innerText().catch(() => "");
  return {
    url,
    title,
    signedOut: signedOut > 0 || /sign-in|accounts\.x\.ai/i.test(url),
    hasComposer: hasComposer > 0,
    isAgent:
      /\/imagine\/agent/i.test(url) ||
      /Imagine Agent/i.test(title) ||
      /Agent Mode/i.test(bodyText.slice(0, 200)),
    bodyPreview: bodyText.replace(/\s+/g, " ").slice(0, 400),
  };
}

async function collectAssetSrcs(page) {
  return page.evaluate(() => {
    const out = [];
    for (const img of document.querySelectorAll("img")) {
      const src = img.currentSrc || img.src || "";
      if (!src) continue;
      const nw = img.naturalWidth || 0;
      const nh = img.naturalHeight || 0;
      const rect = img.getBoundingClientRect();
      const dw = Math.round(rect.width || img.width || 0);
      const dh = Math.round(rect.height || img.height || 0);
      const alt = (img.alt || "").toLowerCase();
      const isGeneratedAlt = alt.includes("generated");
      const isGrokHost = /assets\.grok\.com\/.*\/generated\//i.test(src);
      const isBlob = src.startsWith("blob:");
      const isDataStill = src.startsWith("data:image/");
      // Sidebar history thumbs: huge natural size, ~50px display — exclude unless Generated alt
      // or main canvas display size.
      const visibleMain = dw >= 180 && dh >= 180;
      if (!isGeneratedAlt && !visibleMain) continue;
      if (!(isGrokHost || isBlob || isDataStill || isGeneratedAlt)) continue;
      out.push({
        src,
        nw,
        nh,
        w: dw,
        h: dh,
        alt: img.alt || "",
        isGeneratedAlt,
      });
    }
    return out;
  });
}

async function goCleanImagine(page) {
  await goCleanImagineHome(page);
}

async function forceImageMode(page) {
  const r = await selectGenerationMode(page, "Image");
  if (r.ok) {
    await setImageQuality(page);
    await setAspect169(page);
  }
  return r.ok ? r.how : "none";
}

async function forceAgentMode(page) {
  const r = await selectGenerationMode(page, "Agent");
  return r.ok ? r.how : "none";
}

async function typePrompt(page, text) {
  let composer = page.getByRole("textbox", { name: /ask grok|prompt|imagine/i });
  if (!(await composer.count())) {
    composer = page.locator(
      '[role="textbox"][aria-label*="Ask" i], .tiptap.ProseMirror, [contenteditable="true"], textarea'
    );
  }
  if (!(await composer.count())) return false;
  const box = composer.first();
  await box.click({ force: true });
  await page.keyboard.press("Control+A").catch(() => {});
  await page.keyboard.press("Backspace").catch(() => {});
  // TipTap often ignores fill
  await page.keyboard.type(text, { delay: 8 });
  await page.waitForTimeout(400);
  return true;
}

async function submitPrompt(page) {
  return submitImagine(page);
}

function assetKey(a) {
  // data: URLs are huge; fingerprint by length + head/tail
  const s = a.src || "";
  if (s.startsWith("data:")) {
    return `data:${a.nw}x${a.nh}:${s.length}:${s.slice(0, 64)}:${s.slice(-32)}`;
  }
  return s.split("?")[0];
}

async function waitForNewAssets(page, beforeSrcs, { timeoutMs = 180000 } = {}) {
  const before = new Set(beforeSrcs.map(assetKey));
  const start = Date.now();
  // Generation usually needs a few seconds; avoid grabbing loading stubs
  await page.waitForTimeout(4000);
  while (Date.now() - start < timeoutMs) {
    await page.waitForTimeout(2000);
    const now = await collectAssetSrcs(page);
    const fresh = now.filter((x) => {
      const key = assetKey(x);
      if (before.has(key)) return false;
      // Hard floor: ignore tiny placeholders (e.g. 171x256 stubs)
      if (x.nw < 512 || x.nh < 512) return false;
      // Must be Generated alt and/or main-canvas display size
      if (!(x.isGeneratedAlt || (x.w >= 180 && x.h >= 180))) return false;
      return true;
    });
    fresh.sort((a, b) => {
      const aGen = a.isGeneratedAlt ? 1 : 0;
      const bGen = b.isGeneratedAlt ? 1 : 0;
      if (bGen !== aGen) return bGen - aGen;
      return b.nw * b.nh - a.nw * a.nh;
    });
    if (fresh.length) return fresh;
  }
  return [];
}

async function downloadAsset(page, asset, label = "image") {
  const outFile = path.join(OUT, `grok_imagine_${label}_${stamp()}.png`);
  const src = asset.src;
  try {
    if (src.startsWith("data:")) {
      fs.writeFileSync(outFile, Buffer.from(src.split(",")[1], "base64"));
      return outFile;
    }
    if (src.startsWith("blob:")) {
      const buf = await page.evaluate(async (s) => {
        const res = await fetch(s);
        const ab = await res.arrayBuffer();
        return Array.from(new Uint8Array(ab));
      }, src);
      fs.writeFileSync(outFile, Buffer.from(buf));
      return outFile;
    }
    // page.request shares cookies for assets.grok.com
    const res = await page.request.get(src);
    if (!res.ok()) throw new Error(`HTTP ${res.status()}`);
    fs.writeFileSync(outFile, await res.body());
    return outFile;
  } catch (e) {
    // last resort: screenshot largest matching img
    const imgs = page.locator('img[src*="assets.grok.com"]');
    const n = await imgs.count();
    for (let i = n - 1; i >= 0; i--) {
      const el = imgs.nth(i);
      const s = await el.getAttribute("src");
      if (s && s.includes(src.slice(0, 40))) {
        await el.screenshot({ path: outFile });
        return outFile;
      }
    }
    throw e;
  }
}

async function generateImageMode(page) {
  await goCleanImagine(page);
  const info0 = await pageInfo(page);
  if (info0.signedOut) return { ok: false, reason: "signed_out", info: info0 };

  // If already on agent URL, leave it
  if (info0.isAgent || /\/imagine\/agent/i.test(page.url())) {
    await goCleanImagine(page);
  }

  const modeHow = await forceImageMode(page);
  const before = await collectAssetSrcs(page);
  const typed = await typePrompt(page, PROMPT);
  if (!typed) {
    return {
      ok: false,
      reason: "no_composer",
      shot: await snapshot(page, "no_composer"),
      info: await pageInfo(page),
    };
  }

  // Prefer count=1
  const countBtn = page.getByRole("button", { name: /image count|count/i });
  if (await countBtn.count()) {
    await countBtn.first().click().catch(() => {});
    const one = page.getByRole("option", { name: String(WANT_COUNT) });
    if (await one.count()) await one.first().click().catch(() => {});
    await page.keyboard.press("Escape").catch(() => {});
  }

  const beforeShot = await snapshot(page, "before_submit_image");
  const submitHow = await submitPrompt(page);

  // Must not silently jump to agent without assets — wait for new generated assets
  const fresh = await waitForNewAssets(page, before, { timeoutMs: 180000 });
  const afterShot = await snapshot(page, "after_generate_image");
  const info = await pageInfo(page);

  if (!fresh.length) {
    return {
      ok: false,
      reason: "timeout_no_new_asset",
      modeHow,
      submitHow,
      beforeShot,
      afterShot,
      info,
      beforeCount: before.length,
    };
  }

  const saved = [];
  for (const asset of fresh.slice(0, WANT_COUNT)) {
    saved.push(await downloadAsset(page, asset, "still"));
  }

  return {
    ok: true,
    path: "image_mode",
    modeHow,
    submitHow,
    saved,
    src: fresh[0].src.slice(0, 160),
    dims: `${fresh[0].nw}x${fresh[0].nh}`,
    beforeShot,
    afterShot,
    prompt: PROMPT,
    info,
  };
}

async function generateAgentMode(page) {
  await goCleanImagine(page);
  const info0 = await pageInfo(page);
  if (info0.signedOut) return { ok: false, reason: "signed_out", info: info0 };

  const modeHow = await forceAgentMode(page);
  const before = await collectAssetSrcs(page);
  // Agent briefs work better as goals, not pure camera specs
  const brief =
    process.env.GROK_PROMPT ||
    `Create exactly 1 photoreal concept image only (no video): a single glossy blue marble on a clean white studio surface, soft shadow, high detail. Stop after one still.`;

  const typed = await typePrompt(page, brief);
  if (!typed) {
    return {
      ok: false,
      reason: "no_composer",
      shot: await snapshot(page, "agent_no_composer"),
    };
  }
  const beforeShot = await snapshot(page, "before_submit_agent");
  const submitHow = await submitPrompt(page);

  // Agent can take longer; wait for canvas assets
  const fresh = await waitForNewAssets(page, before, { timeoutMs: 300000 });
  const afterShot = await snapshot(page, "after_generate_agent");
  if (!fresh.length) {
    return {
      ok: false,
      reason: "timeout_no_new_asset",
      path: "agent_mode",
      modeHow,
      submitHow,
      beforeShot,
      afterShot,
      info: await pageInfo(page),
    };
  }
  const saved = [await downloadAsset(page, fresh[0], "agent")];
  return {
    ok: true,
    path: "agent_mode",
    modeHow,
    submitHow,
    saved,
    src: fresh[0].src.slice(0, 160),
    dims: `${fresh[0].nw}x${fresh[0].nh}`,
    beforeShot,
    afterShot,
    prompt: brief,
  };
}

const browser = await chromium.connectOverCDP(CDP);
const page = await getPage(browser);

if (MODE === "status") {
  await goCleanImagine(page);
  const info = await pageInfo(page);
  const shot = await snapshot(page, "status");
  console.log(JSON.stringify({ mode: MODE, ...info, shot }, null, 2));
  process.exit(info.signedOut ? 2 : 0);
}

if (MODE === "generate" || MODE === "generate-image") {
  const result = await generateImageMode(page);
  console.log(JSON.stringify(result, null, 2));
  process.exit(result.ok ? 0 : 3);
}

if (MODE === "generate-agent") {
  const result = await generateAgentMode(page);
  console.log(JSON.stringify(result, null, 2));
  process.exit(result.ok ? 0 : 3);
}

console.error("Unknown mode:", MODE);
process.exit(1);

/**
 * Continue an EXISTING Grok Imagine Agent project (character lock).
 * Never New Generation / home Video — that mints a new project and drifts faces.
 *
 * Env: GROK_AGENT_URL (required, must include ?conversation=),
 *      GROK_NUDGE or GROK_NUDGE_FILE, GROK_OUT,
 *      GROK_EXPECT_PANELS (new clips to wait for), GROK_WAIT_MS
 */
import { chromium } from "playwright-core";
import fs from "fs";
import path from "path";
import { spawnSync } from "child_process";

const CDP = process.env.GROK_CDP || "http://127.0.0.1:9222";
const URL = (process.env.GROK_AGENT_URL || "").trim();
const OUT = process.env.GROK_OUT;
const EXPECT = Number(process.env.GROK_EXPECT_PANELS || "2");
const WAIT_MS = Number(process.env.GROK_WAIT_MS || 12 * 60 * 1000);
const NUDGE =
  process.env.GROK_NUDGE ||
  (process.env.GROK_NUDGE_FILE
    ? fs.readFileSync(process.env.GROK_NUDGE_FILE, "utf8")
    : "");

if (!URL || !/\/imagine\/agent\//i.test(URL)) {
  console.error(JSON.stringify({ ok: false, reason: "GROK_AGENT_URL required (/imagine/agent/{uuid})" }));
  process.exit(2);
}
if (!/[?&]conversation=/i.test(URL)) {
  console.error(
    JSON.stringify({
      ok: false,
      reason: "conversation_query_required",
      hint: "Workspace UUID can be reused across films. Pass ?conversation= from the pack agent_url.txt / user URL.",
    }),
  );
  process.exit(2);
}
if (!OUT) {
  console.error(JSON.stringify({ ok: false, reason: "GROK_OUT required" }));
  process.exit(2);
}
if (!NUDGE.trim()) {
  console.error(JSON.stringify({ ok: false, reason: "GROK_NUDGE or GROK_NUDGE_FILE required" }));
  process.exit(2);
}

fs.mkdirSync(OUT, { recursive: true });
fs.mkdirSync(path.join(OUT, "frames"), { recursive: true });

async function collectUuids(page) {
  return page.evaluate(() => {
    function uuidFrom(src) {
      const m = String(src || "").match(/generated\/([a-f0-9-]{20,})/i);
      return m ? m[1] : null;
    }
    const out = [];
    for (const v of document.querySelectorAll("video")) {
      const src = v.currentSrc || v.src || "";
      const id = uuidFrom(src);
      const r = v.getBoundingClientRect();
      if (id && /assets\.grok\.com|generated_video/i.test(src)) {
        out.push({
          uuid: id,
          src,
          w: v.videoWidth,
          h: v.videoHeight,
          dur: v.duration || 0,
          display: Math.round(r.width * r.height),
        });
      }
    }
    return out;
  });
}

async function findComposer(page) {
  const candidates = [
    page.getByRole("textbox", { name: /ask grok to create|ask grok|imagine|prompt|message/i }),
    page.locator('[role="textbox"][aria-label*="Ask Grok" i]'),
    page.locator(".tiptap.ProseMirror"),
    page.locator("div[contenteditable='true']"),
  ];
  for (const c of candidates) {
    const n = await c.count().catch(() => 0);
    if (!n) continue;
    let best = null;
    let bestScore = -1;
    for (let i = 0; i < Math.min(n, 8); i++) {
      const el = c.nth(i);
      const box = await el.boundingBox().catch(() => null);
      if (!box || box.width < 80 || box.height < 20) continue;
      const score = box.width + box.y * 0.5 + box.height * 2;
      if (score > bestScore) {
        bestScore = score;
        best = el;
      }
    }
    if (best) return best;
  }
  return null;
}

const browser = await chromium.connectOverCDP(CDP);
const ctx = browser.contexts()[0];
if (!ctx) {
  console.error(JSON.stringify({ ok: false, reason: "no_browser_context" }));
  process.exit(2);
}
let page = ctx.pages().find((p) => /imagine\/agent/i.test(p.url())) || ctx.pages()[0] || (await ctx.newPage());
await page.goto(URL, { waitUntil: "domcontentloaded", timeout: 120000 });
await page.waitForTimeout(4000);

if (!/\/imagine\/agent\//i.test(page.url())) {
  console.error(JSON.stringify({ ok: false, reason: "not_on_agent_url", url: page.url() }));
  process.exit(7);
}

const before = await collectUuids(page);
const baseline = new Set(before.map((x) => x.uuid));
fs.writeFileSync(path.join(OUT, "baseline_uuids.json"), JSON.stringify([...baseline], null, 2));
console.log(JSON.stringify({ phase: "baseline", url: page.url(), uuidCount: baseline.size }));

const box = await findComposer(page);
if (!box) {
  console.error(JSON.stringify({ ok: false, reason: "no_composer" }));
  process.exit(3);
}
await box.click({ force: true });
await page.keyboard.press("Control+A").catch(() => {});
await page.keyboard.press("Backspace").catch(() => {});
try {
  await page.evaluate(async (t) => {
    await navigator.clipboard.writeText(t);
  }, NUDGE);
  await page.keyboard.press("Control+V");
} catch {
  await page.keyboard.type(NUDGE.slice(0, 3500), { delay: 2 });
}
await page.waitForTimeout(400);
const send = page.locator('button[aria-label="Send"], button[aria-label="Submit"], button[aria-label*="Send" i]');
if (await send.count()) {
  const btn = send.first();
  if (!(await btn.isDisabled().catch(() => false))) await btn.click();
  else await page.keyboard.press("Control+Enter");
} else {
  await page.keyboard.press("Control+Enter");
}
await page.waitForTimeout(3000);
const afterShot = path.join(OUT, `after_nudge_${Date.now()}.png`);
await page.screenshot({ path: afterShot, fullPage: false }).catch(() => {});
console.log(JSON.stringify({ phase: "nudged", url: page.url(), afterShot }));

const start = Date.now();
let lastNew = [];
while (Date.now() - start < WAIT_MS) {
  await page.mouse.wheel(0, 800).catch(() => {});
  await page.waitForTimeout(8000);
  const now = await collectUuids(page);
  const fresh = now.filter((x) => !baseline.has(x.uuid));
  const uniq = [...new Map(fresh.map((x) => [x.uuid, x])).values()];
  lastNew = uniq;
  console.log(
    JSON.stringify({
      t: Math.round((Date.now() - start) / 1000),
      url: page.url(),
      newUuids: uniq.length,
      ids: uniq.map((x) => x.uuid.slice(0, 12)),
    }),
  );
  if (uniq.length >= EXPECT) break;
}

if (lastNew.length < EXPECT) {
  fs.writeFileSync(
    path.join(OUT, "continue_report.json"),
    JSON.stringify({ ok: false, reason: "timeout", new: lastNew }, null, 2),
  );
  console.log(JSON.stringify({ ok: false, reason: "timeout", newCount: lastNew.length, expect: EXPECT }));
  process.exit(4);
}

const saved = [];
for (const clip of lastNew.slice(0, EXPECT + 2)) {
  const dest = path.join(OUT, `${clip.uuid.slice(0, 12)}.mp4`);
  try {
    const res = await page.request.get(clip.src);
    if (!res.ok()) continue;
    fs.writeFileSync(dest, await res.body());
    const frame = path.join(OUT, "frames", `${clip.uuid.slice(0, 12)}.jpg`);
    spawnSync("ffmpeg", ["-y", "-ss", "2", "-i", dest, "-frames:v", "1", "-q:v", "3", frame], { encoding: "utf8" });
    saved.push({ uuid: clip.uuid, file: dest, frame, bytes: fs.statSync(dest).size });
  } catch (e) {
    saved.push({ uuid: clip.uuid, ok: false, error: String(e).slice(0, 120) });
  }
}

fs.writeFileSync(path.join(OUT, "continue_report.json"), JSON.stringify({ ok: true, saved, url: page.url() }, null, 2));
console.log(JSON.stringify({ ok: true, savedCount: saved.length, saved }, null, 2));
process.exit(saved.length ? 0 : 4);

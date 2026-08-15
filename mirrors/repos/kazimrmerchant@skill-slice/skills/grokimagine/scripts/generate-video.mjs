/**
 * Grok Imagine Video (T2V or I2V) via real Chrome CDP.
 * Usage:
 *   $env:GROK_OUT = "..."
 *   $env:GROK_PROMPT = "motion + one camera move..."
 *   $env:GROK_IMAGE = "path\to\still.png"   # optional — set for I2V (preferred engaging)
 *   $env:GROK_VIDEO_RES = "1080p"           # 480p|720p|1080p
 *   $env:GROK_VIDEO_DUR = "10s"             # 6s|10s|15s
 *   $env:GROK_VIDEO_AUDIO = "1"             # 1=on (SFX/dialogue), 0=off (Remotion VO)
 *   $env:GROK_FIRE_ONLY = "1"               # submit + confirm start + close tab; no MP4 wait
 *   $env:GROK_CLOSE_TAB = "1"               # with FIRE_ONLY (default 1)
 *   node generate-video.mjs
 */
import { chromium } from "playwright-core";
import fs from "fs";
import path from "path";
import {
  attachReferenceImages,
  ensureOneImagineTab,
  goCleanImagineHome,
  selectGenerationMode,
  setAspect169,
  setVideoAudio,
  setVideoPrefs,
  submitImagine,
} from "./ui-mode.mjs";

const CDP = process.env.GROK_CDP || "http://127.0.0.1:9222";
const OUT = process.env.GROK_OUT || "C:\\Users\\user\\.cursor\\grok-chrome\\out";
const IMAGE = process.env.GROK_IMAGE || "";
const PROMPT =
  process.env.GROK_PROMPT ||
  "Subtle cinematic motion, locked tripod, gentle breathing, mouth stays fully closed, no talking, no singing, soft light drift, photoreal 16:9";
const WAIT_MS = Number(process.env.GROK_WAIT_MS || "360000");
const VIDEO_RES = process.env.GROK_VIDEO_RES || "1080p";
const VIDEO_DUR = process.env.GROK_VIDEO_DUR || "10s";
const VIDEO_AUDIO = !["0", "false", "off", "no"].includes(
  String(process.env.GROK_VIDEO_AUDIO || "1").toLowerCase(),
);
const FIRE_ONLY = ["1", "true", "yes", "on"].includes(
  String(process.env.GROK_FIRE_ONLY || "").toLowerCase(),
);

function findPackAgentUrl(startDir) {
  let dir = path.resolve(startDir);
  for (let i = 0; i < 6; i++) {
    const p = path.join(dir, "agent_url.txt");
    if (fs.existsSync(p)) {
      const u = fs.readFileSync(p, "utf8").trim().split(/\r?\n/)[0].trim();
      if (/\/imagine\/agent\//i.test(u)) return { url: u, file: p };
    }
    const parent = path.dirname(dir);
    if (parent === dir) break;
    dir = parent;
  }
  return null;
}

const ALLOW_HOME_VIDEO = ["1", "true", "yes", "on"].includes(
  String(process.env.GROK_ALLOW_HOME_VIDEO || "").toLowerCase(),
);
if (!ALLOW_HOME_VIDEO) {
  const envAgent = (process.env.GROK_AGENT_URL || "").trim();
  const packAgent = findPackAgentUrl(OUT);
  const agentUrl = /\/imagine\/agent\//i.test(envAgent) ? envAgent : packAgent?.url;
  if (agentUrl) {
    console.error(
      JSON.stringify({
        ok: false,
        reason: "series_must_continue_agent",
        agentUrl,
        hint: "Home Video I2V (New Generation) mints a new project and drifts characters. Use agent-continue.mjs on GROK_AGENT_URL. Override only with GROK_ALLOW_HOME_VIDEO=1 for unrelated one-off clips.",
      }),
    );
    process.exit(8);
  }
}

fs.mkdirSync(OUT, { recursive: true });

function stamp() {
  return new Date().toISOString().replace(/[:.]/g, "-");
}

async function snapshot(page, label) {
  const file = path.join(OUT, `${stamp()}_${label}.png`);
  try {
    await page.screenshot({ path: file, fullPage: false, timeout: 15000 });
    return file;
  } catch {
    return null;
  }
}

async function getPage(browser) {
  const context = browser.contexts()[0] || (await browser.newContext());
  const keepTabs = FIRE_ONLY || ["1", "true", "yes", "on"].includes(
    String(process.env.GROK_KEEP_TABS || "").toLowerCase(),
  );
  if (keepTabs) {
    // Prefer an idle Imagine home tab; never close generating /post/ tabs
    let page = context
      .pages()
      .find(
        (p) =>
          /grok\.com\/imagine\/?(\?|$|#)/i.test(p.url()) &&
          !/\/imagine\/(post|agent)\//i.test(p.url()),
      );
    if (!page) {
      page = await context.newPage();
      await page.goto("https://grok.com/imagine", {
        waitUntil: "domcontentloaded",
        timeout: 60000,
      });
      await page.waitForTimeout(1500);
    } else {
      await page.bringToFront().catch(() => {});
    }
    return page;
  }
  let page = await ensureOneImagineTab(context);
  if (!page) {
    page =
      context.pages().find((p) => /grok\.com|accounts\.x\.ai/i.test(p.url())) ||
      context.pages()[0];
  }
  if (!page) page = await context.newPage();
  return page;
}

async function forceVideoMode(page) {
  const r = await selectGenerationMode(page, "Video");
  if (r.ok) {
    await setVideoPrefs(page, { resolution: VIDEO_RES, duration: VIDEO_DUR });
    await setVideoAudio(page, VIDEO_AUDIO);
    await setAspect169(page);
  }
  return r.ok ? r.how : "none";
}

async function typePrompt(page, text) {
  let composer = page.getByRole("textbox", { name: /ask grok|prompt|imagine|type to imagine/i });
  if (!(await composer.count())) {
    composer = page.locator(
      '[role="textbox"][aria-label*="Ask" i], [role="textbox"][aria-label*="imagine" i], .tiptap.ProseMirror, [contenteditable="true"], textarea',
    );
  }
  if (!(await composer.count())) return false;
  const box = composer.first();
  await box.click({ force: true });
  await page.waitForTimeout(200);
  await page.keyboard.press("Control+A").catch(() => {});
  await page.keyboard.press("Backspace").catch(() => {});
  // Clipboard paste is more reliable than keyboard.type for long Imagine prompts
  try {
    await page.evaluate(async (t) => {
      await navigator.clipboard.writeText(t);
    }, text);
    await page.keyboard.press("Control+V");
  } catch {
    await page.keyboard.insertText(text).catch(async () => {
      await page.keyboard.type(text, { delay: 2 });
    });
  }
  await page.waitForTimeout(500);
  const got = ((await box.innerText().catch(() => "")) || (await box.inputValue().catch(() => "")) || "").trim();
  if (got.length < Math.min(40, text.length * 0.5)) {
    // retry insertText
    await box.click({ force: true });
    await page.keyboard.press("Control+A").catch(() => {});
    await page.keyboard.insertText(text).catch(() => {});
    await page.waitForTimeout(400);
  }
  const final = ((await box.innerText().catch(() => "")) || "").trim();
  return final.length >= Math.min(30, text.length * 0.4);
}

async function submitPrompt(page) {
  const how = await submitImagine(page);
  if (how !== "enter") return how;
  const gen = page.getByRole("button", { name: /generate|submit/i });
  if (await gen.count()) {
    const btn = gen.first();
    if (!(await btn.isDisabled().catch(() => false))) {
      await btn.click();
      return "click-generate";
    }
  }
  await page.keyboard.press("Enter");
  return "enter";
}

async function attachImage(page, imagePath) {
  if (!imagePath || !fs.existsSync(imagePath)) {
    return { ok: false, reason: "missing_image" };
  }
  const abs = path.resolve(imagePath);

  // Prefer native file input
  const inputs = page.locator('input[type="file"]');
  const n = await inputs.count();
  if (n > 0) {
    await inputs.first().setInputFiles(abs);
    await page.waitForTimeout(1500);
    return { ok: true, how: "input-file", count: n };
  }

  // Click attach / plus / image buttons then set files via chooser
  const attachCandidates = [
    page.getByRole("button", { name: /attach|upload|add image|image|photo|reference|media/i }),
    page.locator('button[aria-label*="Attach" i], button[aria-label*="Upload" i], button[aria-label*="image" i]'),
  ];
  for (const loc of attachCandidates) {
    if (!(await loc.count())) continue;
    try {
      const [chooser] = await Promise.all([
        page.waitForEvent("filechooser", { timeout: 4000 }),
        loc.first().click({ force: true }),
      ]);
      await chooser.setFiles(abs);
      await page.waitForTimeout(1500);
      return { ok: true, how: "filechooser" };
    } catch {
      /* try next */
    }
  }

  return { ok: false, reason: "no_file_input" };
}

async function collectVideos(page) {
  try {
    return await page.evaluate(() => {
      const out = [];
      for (const v of document.querySelectorAll("video")) {
        const src = v.currentSrc || v.src || "";
        if (!src) continue;
        const r = v.getBoundingClientRect();
        const uuidMatch = src.match(/generated\/([a-f0-9-]{20,})/i);
        out.push({
          src: src.slice(0, 600),
          uuid: uuidMatch ? uuidMatch[1] : null,
          w: v.videoWidth || 0,
          h: v.videoHeight || 0,
          dur: v.duration || 0,
          displayW: Math.round(r.width),
          displayH: Math.round(r.height),
          hosted: /assets\.grok\.com|imagine-public\.x\.ai/i.test(src),
        });
      }
      return out;
    });
  } catch {
    return [];
  }
}

async function waitForNewVideo(page, beforeSrcs, timeoutMs) {
  const before = new Set(beforeSrcs);
  const start = Date.now();
  await page.waitForTimeout(5000);
  while (Date.now() - start < timeoutMs) {
    await page.waitForTimeout(2500);
    // Allow SPA navigation to /post/ to settle
    if (page.isClosed()) return [];
    try {
      await page.waitForLoadState("domcontentloaded", { timeout: 5000 }).catch(() => {});
    } catch {
      /* ignore */
    }
    const now = await collectVideos(page);
    const fresh = now.filter(
      (v) =>
        v.hosted &&
        !before.has(v.src) &&
        (v.displayW >= 200 || v.w >= 640 || /generated_video\.mp4/i.test(v.src)),
    );
    // Prefer large on-canvas videos over 50px history thumbs
    const big = fresh.filter((v) => v.displayW >= 200 || v.w >= 640);
    const pool = big.length ? big : fresh;
    if (pool.length) {
      pool.sort((a, b) => b.displayW * b.displayH - a.displayW * a.displayH);
      return pool;
    }
    let hrefs = [];
    try {
      hrefs = await page.evaluate(() =>
        [...document.querySelectorAll("a[href], video source, video")]
          .map((el) => el.href || el.src || el.currentSrc || "")
          .filter((s) => /generated_video\.mp4|assets\.grok\.com.*generated/i.test(s)),
      );
    } catch {
      hrefs = [];
    }
    const linkFresh = hrefs.filter((h) => !before.has(h));
    if (linkFresh.length) {
      return linkFresh.map((src) => ({
        src,
        uuid: (src.match(/generated\/([a-f0-9-]{20,})/i) || [])[1] || null,
        hosted: true,
        displayW: 0,
        displayH: 0,
        w: 0,
        h: 0,
        dur: 0,
      }));
    }
    // Progress still running?
    const generating = await page
      .evaluate(() => /Generating\s+\d{1,3}\s*%/i.test(document.body?.innerText || ""))
      .catch(() => false);
    if (!generating && Date.now() - start > 45000) {
      // one more pass for large video after progress gone
      const late = (await collectVideos(page)).filter(
        (v) => v.hosted && (v.displayW >= 320 || v.w >= 640) && !before.has(v.src),
      );
      if (late.length) {
        late.sort((a, b) => b.displayW * b.displayH - a.displayW * a.displayH);
        return late;
      }
    }
  }
  return [];
}

async function downloadVideo(page, video) {
  const short = (video.uuid || "vid").slice(0, 12);
  const outFile = path.join(OUT, `grok_video_${short}_${stamp()}.mp4`);
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
  if (!res.ok()) throw new Error(`HTTP ${res.status()} for ${src.slice(0, 80)}`);
  fs.writeFileSync(outFile, await res.body());
  return outFile;
}

const browser = await chromium.connectOverCDP(CDP);
let page = await getPage(browser);

if (FIRE_ONLY) {
  // Never New-Generation a /post/ tab (cancels in-flight video). Use idle home only.
  if (/\/imagine\/(post|agent)\//i.test(page.url())) {
    page = await page.context().newPage();
    await page.goto("https://grok.com/imagine", {
      waitUntil: "domcontentloaded",
      timeout: 60000,
    });
    await page.waitForTimeout(2000);
  } else if (!/grok\.com\/imagine/i.test(page.url())) {
    await page.goto("https://grok.com/imagine", {
      waitUntil: "domcontentloaded",
      timeout: 60000,
    });
    await page.waitForTimeout(2000);
  }
} else {
  await goCleanImagineHome(page);
}

const signedOut = await page
  .locator('button:has-text("Sign in"), a:has-text("Sign in")')
  .count()
  .catch(() => 0);
if (signedOut > 0 || /accounts\.x\.ai/i.test(page.url())) {
  console.log(JSON.stringify({ ok: false, reason: "signed_out", url: page.url() }, null, 2));
  process.exit(2);
}

let modeHow = await forceVideoMode(page);
if (modeHow === "none") {
  await goCleanImagineHome(page);
  await page.waitForTimeout(1500);
  modeHow = await forceVideoMode(page);
}
if (modeHow === "none") {
  console.log(
    JSON.stringify(
      {
        ok: false,
        reason: "video_mode_failed",
        shot: await snapshot(page, "video_mode_failed"),
        url: page.url(),
      },
      null,
      2,
    ),
  );
  process.exit(6);
}

const beforeVideos = (await collectVideos(page)).map((v) => v.src);

let attach = { ok: true, how: "none", count: 0 };
if (IMAGE) {
  attach = await attachReferenceImages(page, IMAGE);
  if (!attach.ok) {
    // fallback to legacy attachImage if helper fails
    attach = await attachImage(page, IMAGE);
  }
  if (!attach.ok) {
    console.log(
      JSON.stringify(
        {
          ok: false,
          reason: attach.reason,
          modeHow,
          shot: await snapshot(page, "no_attach"),
        },
        null,
        2,
      ),
    );
    process.exit(3);
  }
}

const typed = await typePrompt(page, PROMPT);
if (!typed) {
  console.log(
    JSON.stringify(
      { ok: false, reason: "no_composer", modeHow, attach, shot: await snapshot(page, "no_composer") },
      null,
      2,
    ),
  );
  process.exit(3);
}

const beforeShot = await snapshot(page, "before_submit_video");
const submitHow = await submitPrompt(page);
await page.waitForTimeout(3000);
// Bind to this generation: must land on /post/ with our prompt still visible (or Generating %)
const postUrl = page.url();
const bound = await page.evaluate((needle) => {
  const text = document.body?.innerText || "";
  const generating = /Generating\s+\d{1,3}\s*%/i.test(text);
  const hasNeedle = needle.split(/\s+/).filter((w) => w.length > 5).slice(0, 4).some((w) => text.includes(w));
  return { generating, hasNeedle, textHead: text.slice(0, 200) };
}, PROMPT.slice(0, 80));
if (!/\/imagine\/post\//i.test(postUrl) && !bound.generating) {
  console.log(
    JSON.stringify({
      ok: false,
      reason: "submit_did_not_open_post",
      submitHow,
      postUrl,
      bound,
      beforeShot,
      shot: await snapshot(page, "submit_unbound"),
    }),
  );
  process.exit(7);
}

// Parallel fire: submit on a dedicated tab and LEAVE IT GENERATING.
// Do NOT click New Generation on that tab (cancels the job). Prefer new tab for next fire.
if (FIRE_ONLY) {
  await page.waitForTimeout(4000);
  const url = page.url();
  const started =
    /\/imagine\/post\//i.test(url) ||
    (await page
      .evaluate(() => /%|generating|progress|queued/i.test(document.body.innerText || ""))
      .catch(() => false));
  const afterShot = await snapshot(page, "fire_only_after_submit");
  const closeTab = ["1", "true", "yes", "on"].includes(
    String(process.env.GROK_CLOSE_TAB || "0").toLowerCase(),
  );
  let freedHow = "leave_generating_tab";
  if (closeTab) {
    // Only close if sibling tabs exist AND generation already clearly past submit URL
    const sibs = page.context().pages().filter((p) => p !== page);
    if (sibs.length > 0 && /\/imagine\/post\//i.test(url)) {
      // leave generating — do not close; next job should use newPage
      freedHow = "kept_generating_tab";
    } else {
      freedHow = "kept_generating_tab_no_siblings";
    }
  }
  // Open a fresh Imagine home tab for the next fire (does not cancel this post)
  try {
    const next = await page.context().newPage();
    await next.goto("https://grok.com/imagine", {
      waitUntil: "domcontentloaded",
      timeout: 60000,
    });
    freedHow = "opened_next_imagine_tab";
  } catch {
    freedHow = "leave_generating_tab";
  }
  console.log(
    JSON.stringify({
      ok: true,
      path: IMAGE ? "i2v" : "t2v",
      fireOnly: true,
      started: !!started,
      submitHow,
      modeHow,
      attach,
      url,
      freedHow,
      beforeShot,
      afterShot,
      prompt: PROMPT,
      image: IMAGE || null,
      prefs: { VIDEO_RES, VIDEO_DUR, VIDEO_AUDIO },
      note: "Leave post tab generating; harvest UUID later. Do not New Generation on fire tab.",
    }),
  );
  process.exit(0);
}

const fresh = await waitForNewVideo(page, beforeVideos, WAIT_MS);
const afterShot = await snapshot(page, "after_generate_video");

// Reject wrong-session harvest: must still be on a post and prompt-ish text
const guard = await page.evaluate((needle) => {
  const text = document.body?.innerText || "";
  const words = needle.split(/\s+/).filter((w) => w.length > 6).slice(0, 5);
  const hits = words.filter((w) => text.toLowerCase().includes(w.toLowerCase())).length;
  return {
    url: location.href,
    onPost: /\/imagine\/post\//i.test(location.href),
    hits,
    hasSpider: /spider/i.test(text),
  };
}, PROMPT).catch(() => ({ url: page.url(), onPost: false, hits: 0, hasSpider: false }));

if (!fresh.length || (!guard.onPost && !guard.hasSpider) || (guard.hits < 1 && !guard.hasSpider)) {
  console.log(
    JSON.stringify(
      {
        ok: false,
        reason: fresh.length ? "wrong_session_or_unbound_post" : "timeout_no_video",
        guard,
        modeHow,
        attach,
        submitHow,
        beforeShot,
        afterShot,
        beforeCount: beforeVideos.length,
        prefs: { VIDEO_RES, VIDEO_DUR, VIDEO_AUDIO, path: IMAGE ? "i2v" : "t2v" },
      },
      null,
      2,
    ),
  );
  process.exit(4);
}

const saved = [];
for (const v of fresh.slice(0, 1)) {
  saved.push(await downloadVideo(page, v));
}

console.log(
  JSON.stringify(
    {
      ok: true,
      path: IMAGE ? "i2v" : "t2v",
      modeHow,
      attach,
      submitHow,
      saved,
      video: fresh[0],
      beforeShot,
      afterShot,
      prompt: PROMPT,
      image: IMAGE || null,
      prefs: { VIDEO_RES, VIDEO_DUR, VIDEO_AUDIO },
    },
    null,
    2,
  ),
);
process.exit(0);

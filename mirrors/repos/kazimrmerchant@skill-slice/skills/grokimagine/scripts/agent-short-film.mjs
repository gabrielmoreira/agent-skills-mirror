/**
 * Drive Grok Imagine Agent Mode for a short film brief.
 * Modes: status | start | wait | download | snapshot | nudge | stitch
 *
 * Critical:
 * - Detect SuperGrok #subscribe / upgrade modal → stop (exit 6), do not claim success
 * - Detect SuperGrok #subscribe / upgrade modal → stop (exit 6), do not claim success
 * - start success requires URL /imagine/agent/ + brief keywords in page body
 * - wait counts videos only from CURRENT agent conversation (not sidebar history)
 * - Prefer New Generation → Agent radio → Short Film template before typing
 *   ONLY when starting a brand-new film. Series extra beats: GROK_AGENT_URL
 *   + nudge / agent-continue.mjs — never New Generation (character drift).
 * - Optional GROK_BRIEF_MAX chars for TipTap long-paste failures
 */
import { chromium } from "playwright-core";
import fs from "fs";
import path from "path";
import { selectGenerationMode } from "./ui-mode.mjs";


function requireEnv(name) {
  const v = (process.env[name] || "").trim();
  if (!v) {
    console.error(`Set ${name} to a local path. This script has no machine default.`);
    process.exit(2);
  }
  return v;
}

const CDP = process.env.GROK_CDP || "http://127.0.0.1:9222";
/** Existing Agent project — set this to continue a series. Never New Generation. */
const AGENT_URL = (process.env.GROK_AGENT_URL || "").trim();
const OUT = requireEnv("GROK_OUT");
const BRIEF_PATH = requireEnv("GROK_BRIEF");
const MODE = process.argv[2] || "status";
const BRIEF_MAX = Number(process.env.GROK_BRIEF_MAX || 0); // 0 = no truncate
const EXPECT_PANELS = Number(process.env.GROK_EXPECT_PANELS || 8);
const KEYWORDS_ENV = process.env.GROK_KEYWORDS || "";

fs.mkdirSync(OUT, { recursive: true });

function stamp() {
  return new Date().toISOString().replace(/[:.]/g, "-");
}

function extractBrief(md) {
  const m = md.match(/## Master Agent brief[\s\S]*?```\r?\n([\s\S]*?)\r?\n```/);
  if (m) return m[1].trim();
  return md.slice(0, 4000);
}

/** Keywords used to prove THIS session's brief is on the page (not history). */
function briefKeywords(brief) {
  if (KEYWORDS_ENV.trim()) {
    return KEYWORDS_ENV.split(",").map((s) => s.trim()).filter(Boolean);
  }
  // Fallback: distinctive long words from brief
  const words = (brief.match(/[A-Za-z][A-Za-z0-9_-]{5,}/g) || [])
    .filter((w) => !/^(PANEL|STORY|STYLE|AUDIO|AFTER|TITLE|ASPECT|SHORT|FILM|EVERY|STILLS|GENERATE|CINEMATIC)$/i.test(w));
  const uniq = [...new Set(words.map((w) => w.toLowerCase()))];
  return uniq.slice(0, 5);
}

function bodyHasKeywords(body, keywords, minHits = 2) {
  if (!keywords.length) return /short film|storyboard|panel/i.test(body);
  let hits = 0;
  for (const k of keywords) {
    if (new RegExp(k.replace(/[.*+?^${}()|[\]\\]/g, "\\$&"), "i").test(body)) hits += 1;
  }
  return hits >= Math.min(minHits, keywords.length);
}

async function getPage(browser) {
  const context = browser.contexts()[0];
  if (!context) throw new Error("no_browser_context — start owned Chrome hub first");
  let page =
    context.pages().find((p) => /grok\.com|accounts\.x\.ai/i.test(p.url())) ||
    context.pages()[0];
  if (!page) page = await context.newPage();
  return page;
}

async function snapshot(page, label) {
  const file = path.join(OUT, `${stamp()}_${label}.png`);
  await page.screenshot({ path: file, fullPage: false }).catch(() => {});
  return file;
}

/**
 * SuperGrok paywall / upgrade modal detection.
 * Prior failure: URL gained #subscribe and agent never ran.
 */
async function detectPaywall(page) {
  const url = page.url();
  const hashSubscribe = /#subscribe/i.test(url);
  const body = await page.locator("body").innerText().catch(() => "");
  const textHit =
    /upgrade to (super)?grok|subscribe to (super)?grok|super.?grok (heavy|plus)?.*(required|upgrade)|unlock (agent|imagine)|get super.?grok/i.test(
      body
    );
  // Modal-ish buttons common on paywall
  const modalBtns = await page
    .locator(
      'button:has-text("Upgrade"), button:has-text("Subscribe"), a:has-text("Upgrade"), a:has-text("Subscribe"), button:has-text("Get SuperGrok")'
    )
    .count()
    .catch(() => 0);
  // Dialog role near subscribe copy
  const dialog = await page.locator('[role="dialog"], [data-state="open"]').count().catch(() => 0);
  const blocked = hashSubscribe || (textHit && (modalBtns > 0 || dialog > 0 || hashSubscribe));
  return {
    blocked: Boolean(blocked || hashSubscribe),
    hashSubscribe,
    textHit,
    modalBtns,
    dialog,
    url,
  };
}

async function pageInfo(page, keywords = []) {
  const url = page.url();
  const title = await page.title().catch(() => "");
  const body = await page.locator("body").innerText().catch(() => "");
  const signedOut = await page
    .locator('button:has-text("Sign in"), a:has-text("Sign in")')
    .count()
    .catch(() => 0);
  const paywall = await detectPaywall(page);
  const isAgentUrl = /\/imagine\/agent\//i.test(url);
  return {
    url,
    title,
    signedOut: signedOut > 0 || /sign-in|accounts\.x\.ai/i.test(url),
    isAgentUrl,
    isAgent: isAgentUrl || /Agent/i.test(title),
    hasBriefKeywords: bodyHasKeywords(body, keywords),
    keywordHits: keywords.filter((k) =>
      new RegExp(k.replace(/[.*+?^${}()|[\]\\]/g, "\\$&"), "i").test(body)
    ),
    paywall,
    bodyPreview: body.replace(/\s+/g, " ").slice(0, 800),
  };
}

async function clickFirst(page, locators) {
  for (const loc of locators) {
    try {
      if (await loc.count()) {
        await loc.first().click({ force: true });
        return true;
      }
    } catch {
      /* try next */
    }
  }
  return false;
}

/**
 * Clean slate: New Generation → Agent mode → Short Film template.
 * ONLY for brand-new films. Never call this when GROK_AGENT_URL is set.
 */
async function forceAgent(page) {
  await page.goto("https://grok.com/imagine", {
    waitUntil: "domcontentloaded",
    timeout: 60000,
  });
  await page.waitForTimeout(2500);

  // Dismiss subscribe hash if we landed with it (won't clear paywall, but cleans URL)
  if (/#subscribe/i.test(page.url())) {
    await page.goto("https://grok.com/imagine", {
      waitUntil: "domcontentloaded",
      timeout: 60000,
    });
    await page.waitForTimeout(1500);
  }

  // New Generation / New chat — avoid hijacking old agent canvas
  await clickFirst(page, [
    page.getByRole("button", { name: /new generation/i }),
    page.getByRole("button", { name: /^new$/i }),
    page.locator('button[aria-label*="New" i]'),
    page.getByRole("link", { name: /new generation/i }),
  ]);
  await page.waitForTimeout(1000);

  // Agent radio: aria-label (unselected Agent often has EMPTY visible text)
  const mode = await selectGenerationMode(page, "Agent");
  const agentOk =
    mode.ok ||
    (await clickFirst(page, [
      page.locator('[role="radio"][aria-label="Agent"]'),
      page.getByRole("radio", { name: /^Agent$/i }),
      page.getByRole("button", { name: /^Agent$/i }),
    ]));
  await page.waitForTimeout(800);

  // Short Film template when visible
  const shortFilmOk = await clickFirst(page, [
    page.getByRole("button", { name: /short film/i }),
    page.getByRole("link", { name: /short film/i }),
    page.locator('[role="button"]:has-text("Short Film")'),
    page.locator('button:has-text("Short film")'),
  ]);
  await page.waitForTimeout(1200);

  // Re-assert Agent after template (UI may reset mode)
  await selectGenerationMode(page, "Agent");
  await page.waitForTimeout(500);

  return { agentOk, shortFilmOk, mode };
}

/**
 * Prefer the main Ask Grok / Imagine composer — not Discover search or sidebar.
 */
async function findComposer(page) {
  const candidates = [
    page.getByRole("textbox", { name: /ask grok to create|ask grok|imagine|prompt|message/i }),
    page.locator('[role="textbox"][aria-label*="Ask Grok" i]'),
    page.locator('[role="textbox"][aria-label*="Imagine" i]'),
    page.locator(".tiptap.ProseMirror"),
    page.locator('[contenteditable="true"][data-placeholder]'),
    page.locator('div[contenteditable="true"]'),
    page.locator("textarea"),
  ];
  for (const c of candidates) {
    const n = await c.count().catch(() => 0);
    if (!n) continue;
    // Prefer largest visible contenteditable near bottom (composer)
    let best = null;
    let bestScore = -1;
    for (let i = 0; i < Math.min(n, 8); i++) {
      const el = c.nth(i);
      const box = await el.boundingBox().catch(() => null);
      if (!box || box.width < 80 || box.height < 20) continue;
      // Prefer wider + lower on page (composer vs top search)
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

async function typePrompt(page, text) {
  const box = await findComposer(page);
  if (!box) return { ok: false, reason: "no_composer" };
  await box.click({ force: true });
  await page.waitForTimeout(200);
  await page.keyboard.press("Control+A").catch(() => {});
  await page.keyboard.press("Backspace").catch(() => {});
  await page.waitForTimeout(150);

  // Prefer clipboard paste for long briefs (TipTap more reliable than type)
  let method = "type";
  try {
    await page.evaluate(async (t) => {
      await navigator.clipboard.writeText(t);
    }, text);
    await page.keyboard.press("Control+V");
    method = "paste";
    await page.waitForTimeout(400);
  } catch {
    const chunks = text.match(/[\s\S]{1,350}/g) || [text];
    for (const c of chunks) {
      await page.keyboard.type(c, { delay: 3 });
    }
    method = "type_chunks";
  }

  // Verify text landed in composer-ish surface
  const body = await page.locator("body").innerText().catch(() => "");
  const sample = text.slice(0, 40).replace(/\s+/g, " ");
  const hasBrief = body.includes(sample.slice(0, 24)) || body.includes(text.slice(20, 50));
  return { ok: true, method, hasBriefPreview: hasBrief };
}

async function submit(page) {
  const send = page.locator(
    'button[aria-label="Send"], button[aria-label="Submit"], button[aria-label*="Send" i]'
  );
  if (await send.count()) {
    const btn = send.first();
    const disabled = await btn.isDisabled().catch(() => false);
    if (!disabled) {
      await btn.click();
      return "send";
    }
  }
  // Ctrl+Enter often submits TipTap
  await page.keyboard.press("Control+Enter").catch(() => {});
  await page.waitForTimeout(400);
  await page.keyboard.press("Enter");
  return "enter";
}

/**
 * Collect media. Canvas videos are often off-screen (large left/x) — do NOT
 * require visibility. Sidebar thumbs: left strip + tiny display width only.
 * Over-filtering left nav caused wait to see 0 videos.
 */
async function collectMedia(page, { sessionOnly = false } = {}) {
  return page.evaluate((sessionOnly) => {
    function inSidebar(el) {
      let n = el;
      for (let i = 0; i < 12 && n; i++) {
        const cls = (n.className && String(n.className)) || "";
        const id = n.id || "";
        const role = n.getAttribute?.("role") || "";
        const aria = n.getAttribute?.("aria-label") || "";
        if (
          /sidebar|history|nav|rail|drawer/i.test(cls + id + aria) ||
          role === "navigation" ||
          n.tagName === "NAV" ||
          n.tagName === "ASIDE"
        ) {
          return true;
        }
        n = n.parentElement;
      }
      const r = el.getBoundingClientRect();
      // Only true left-rail thumbs (not canvas nodes with large layout coords)
      if (r.left >= 0 && r.left < 140 && r.width > 0 && r.width < 100) return true;
      return false;
    }

    function uuidFrom(src) {
      const m = String(src || "").match(/generated\/([a-f0-9-]{20,})/i);
      return m ? m[1] : null;
    }

    function isHostedVideo(src) {
      return /assets\.grok\.com.*generated|imagine-public\.x\.ai/i.test(src || "");
    }

    const imgs = [...document.querySelectorAll("img")].map((i) => {
      const r = i.getBoundingClientRect();
      return {
        kind: "img",
        src: (i.currentSrc || i.src || "").slice(0, 300),
        alt: i.alt || "",
        nw: i.naturalWidth,
        nh: i.naturalHeight,
        w: Math.round(r.width),
        h: Math.round(r.height),
        sidebar: inSidebar(i),
        uuid: uuidFrom(i.currentSrc || i.src),
      };
    });

    const videos = [...document.querySelectorAll("video")].map((v) => {
      const r = v.getBoundingClientRect();
      const src = v.currentSrc || v.src || "";
      const sidebar = inSidebar(v);
      // Canvas clips: hosted generated URL + (display >= 80 OR offscreen layout)
      const canvasLike =
        isHostedVideo(src) &&
        !sidebar &&
        (r.width >= 80 || r.width === 0 || Math.abs(r.left) > 200);
      return {
        kind: "video",
        src: src.slice(0, 500),
        w: v.videoWidth,
        h: v.videoHeight,
        dur: v.duration || 0,
        displayW: Math.round(r.width),
        displayH: Math.round(r.height),
        y: r.top + window.scrollY,
        x: r.left + window.scrollX,
        left: r.left,
        sidebar,
        canvasLike,
        uuid: uuidFrom(src),
      };
    });

    const sessionVideos = videos.filter((v) =>
      sessionOnly ? v.canvasLike || (!v.sidebar && v.uuid) : true
    );

    const links = [...document.querySelectorAll("a[href]")]
      .map((a) => ({ href: a.href, text: (a.innerText || "").slice(0, 40) }))
      .filter((a) => /download|\.mp4|video|export/i.test(a.href + a.text));
    const buttons = [...document.querySelectorAll("button")]
      .map((b) => (b.getAttribute("aria-label") || b.innerText || "").trim())
      .filter((t) => /stitch|animate|export|download|upscale|short film|new agent|generate/i.test(t))
      .slice(0, 40);

    const uniqueVideoUuids = [
      ...new Set(sessionVideos.filter((v) => v.uuid).map((v) => v.uuid)),
    ];

    return {
      imgs: imgs.filter((i) => !sessionOnly || !i.sidebar).slice(0, 60),
      videos: sessionOnly ? sessionVideos : videos,
      links,
      buttons,
      uniqueVideoUuids,
      uniqueMediaUuids: uniqueVideoUuids,
    };
  }, sessionOnly);
}

async function tryClick(page, names) {
  for (const name of names) {
    const loc = page.getByRole("button", { name: new RegExp(name, "i") });
    if (await loc.count()) {
      await loc.first().click({ force: true }).catch(() => {});
      return name;
    }
  }
  for (const name of names) {
    const loc = page.locator(`button[aria-label*="${name}" i]`);
    if (await loc.count()) {
      await loc.first().click({ force: true }).catch(() => {});
      return `aria:${name}`;
    }
  }
  return null;
}

async function downloadVideos(page) {
  const media = await collectMedia(page, { sessionOnly: true });
  const saved = [];
  const seen = new Set();
  for (const v of media.videos) {
    if (v.sidebar) continue;
    const key = v.uuid || v.src;
    if (!key || seen.has(key)) continue;
    seen.add(key);
    if (!v.src || v.src.startsWith("blob:")) {
      if (v.src.startsWith("blob:")) {
        try {
          const buf = await page.evaluate(async (src) => {
            const res = await fetch(src);
            const ab = await res.arrayBuffer();
            return Array.from(new Uint8Array(ab));
          }, v.src);
          const f = path.join(OUT, `agent_video_${stamp()}.mp4`);
          fs.writeFileSync(f, Buffer.from(buf));
          saved.push(f);
        } catch {
          /* skip */
        }
      }
      continue;
    }
    try {
      const res = await page.request.get(v.src);
      if (res.ok()) {
        const short = (v.uuid || "vid").slice(0, 12);
        const f = path.join(OUT, `agent_video_${short}_${stamp()}.mp4`);
        fs.writeFileSync(f, await res.body());
        saved.push(f);
      }
    } catch {
      /* skip */
    }
  }
  return { saved, media };
}

/** Wait until URL is agent session (or timeout). */
async function waitForAgentUrl(page, ms = 45000) {
  const start = Date.now();
  while (Date.now() - start < ms) {
    if (/\/imagine\/agent\//i.test(page.url())) return true;
    await page.waitForTimeout(1000);
  }
  return /\/imagine\/agent\//i.test(page.url());
}

const browser = await chromium.connectOverCDP(CDP);
const page = await getPage(browser);

if (AGENT_URL && /\/imagine\/agent\//i.test(AGENT_URL)) {
  await page.goto(AGENT_URL, { waitUntil: "domcontentloaded", timeout: 120000 });
  await page.waitForTimeout(3500);
}

// Load brief keywords early when brief exists (for wait/status filters)
let keywords = [];
let briefText = "";
if (fs.existsSync(BRIEF_PATH)) {
  try {
    briefText = extractBrief(fs.readFileSync(BRIEF_PATH, "utf8"));
    keywords = briefKeywords(briefText);
  } catch {
    /* ignore */
  }
}

if (MODE === "status" || MODE === "snapshot") {
  const info = await pageInfo(page, keywords);
  const media = await collectMedia(page, { sessionOnly: info.isAgentUrl });
  const shot = await snapshot(page, MODE);
  console.log(
    JSON.stringify(
      {
        mode: MODE,
        info,
        mediaSummary: {
          imgs: media.imgs.length,
          videos: media.videos.length,
          sessionVideos: media.videos.filter((v) => !v.sidebar).length,
          uniqueVideoUuids: media.uniqueVideoUuids?.length || 0,
          buttons: media.buttons,
          videoSrcs: media.videos
            .filter((v) => !v.sidebar)
            .slice(0, 15)
            .map((v) => ({
              src: v.src?.slice(0, 120),
              dur: v.dur,
              w: v.w,
              h: v.h,
              uuid: v.uuid,
              sidebar: v.sidebar,
            })),
        },
        keywords,
        shot,
      },
      null,
      2
    )
  );
  if (info.paywall?.blocked) process.exit(6);
  process.exit(info.signedOut ? 2 : 0);
}

if (MODE === "start") {
  if (AGENT_URL && /\/imagine\/agent\//i.test(AGENT_URL)) {
    console.error(
      JSON.stringify({
        ok: false,
        reason: "do_not_new_generation_on_existing_agent",
        agentUrl: AGENT_URL,
        hint: "start clicks New Generation and drifts characters. Use scripts/agent-continue.mjs or mode nudge.",
      }),
    );
    process.exit(8);
  }
  const md = fs.readFileSync(BRIEF_PATH, "utf8");
  let brief = extractBrief(md);
  brief = brief.replace(/Dana/gi, "").replace(/\s{2,}/g, " ");
  if (BRIEF_MAX > 200 && brief.length > BRIEF_MAX) {
    brief = brief.slice(0, BRIEF_MAX) + "\n\n[Brief truncated for TipTap; continue full 10-panel storyboard in order.]";
  }
  keywords = briefKeywords(brief);

  const forceMeta = await forceAgent(page);
  const paywallBefore = await detectPaywall(page);
  if (paywallBefore.blocked) {
    const shot = await snapshot(page, "paywall_before_start");
    console.log(
      JSON.stringify(
        {
          ok: false,
          reason: "supergrok_paywall",
          paywall: paywallBefore,
          forceMeta,
          shot,
          human:
            "SuperGrok upgrade/subscribe modal detected. Human must confirm SuperHeavy on user@example.com, dismiss #subscribe, then re-run start.",
        },
        null,
        2
      )
    );
    process.exit(6);
  }

  const before = await snapshot(page, "before_brief");
  const typed = await typePrompt(page, brief);
  if (!typed.ok) {
    console.log(JSON.stringify({ ok: false, reason: "no_composer", before, forceMeta }));
    process.exit(3);
  }

  const how = await submit(page);
  // Allow navigation to /imagine/agent/{id}
  const navigated = await waitForAgentUrl(page, 50000);
  await page.waitForTimeout(3000);

  const paywallAfter = await detectPaywall(page);
  const info = await pageInfo(page, keywords);
  const shot = await snapshot(page, "after_submit_agent");

  if (paywallAfter.blocked) {
    console.log(
      JSON.stringify(
        {
          ok: false,
          reason: "supergrok_paywall_after_submit",
          how,
          briefChars: brief.length,
          forceMeta,
          typed,
          info,
          paywall: paywallAfter,
          before,
          shot,
          human: "Submit hit SuperGrok paywall (#subscribe). Do not claim agent started.",
        },
        null,
        2
      )
    );
    process.exit(6);
  }

  // Success gate: agent URL + brief keywords.
  // NOTE: Grok often REUSES the same /imagine/agent/{uuid} workspace across films
  // Workspace id alone ≠ film identity.
  // Prefer keywordHits + later frame QC; conversation= query when present.
  const success =
    info.isAgentUrl &&
    (info.hasBriefKeywords || info.keywordHits.length >= 2) &&
    !info.signedOut;

  // Soft success: agent URL + at least one keyword (stream may lag)
  const softSuccess =
    info.isAgentUrl && navigated && !info.signedOut && info.keywordHits.length >= 1;

  console.log(
    JSON.stringify(
      {
        ok: success || softSuccess,
        strictSuccess: success,
        softSuccess,
        how,
        briefChars: brief.length,
        keywords,
        forceMeta,
        typed,
        navigated,
        info,
        before,
        shot,
        reason: success
          ? "agent_url_and_keywords"
          : softSuccess
            ? "agent_url_only_keywords_pending"
            : !info.isAgentUrl
              ? "no_agent_url"
              : "keywords_missing",
      },
      null,
      2
    )
  );

  if (!success && !softSuccess) {
    // Stay on page for human inspect; exit non-zero
    process.exit(7);
  }
  // Persist session marker for wait mode
  const marker = {
    startedAt: new Date().toISOString(),
    url: info.url,
    keywords,
    briefChars: brief.length,
  };
  fs.writeFileSync(path.join(OUT, "agent_session.json"), JSON.stringify(marker, null, 2));
  process.exit(0);
}

if (MODE === "nudge") {
  const paywall = await detectPaywall(page);
  if (paywall.blocked) {
    const shot = await snapshot(page, "paywall_nudge");
    console.log(JSON.stringify({ ok: false, reason: "supergrok_paywall", paywall, shot }, null, 2));
    process.exit(6);
  }
  const msg =
    process.env.GROK_NUDGE ||
    "Continue this short film. Animate each storyboard panel as a ~6-second cinematic vertical (9:16) clip in order P1 to P10. Keep style lock. Then stitch P1→P10 into one continuous short film with soft crossfades.";
  const typed = await typePrompt(page, msg);
  if (!typed.ok) {
    console.log(JSON.stringify({ ok: false, reason: "no_composer" }));
    process.exit(3);
  }
  const how = await submit(page);
  await page.waitForTimeout(3000);
  const shot = await snapshot(page, "after_nudge");
  console.log(JSON.stringify({ ok: true, how, shot, info: await pageInfo(page, keywords) }, null, 2));
  process.exit(0);
}

if (MODE === "stitch") {
  const clicked = await tryClick(page, ["Stitch", "Export", "Download", "Compile"]);
  await page.waitForTimeout(3000);
  const shot = await snapshot(page, "after_stitch_click");
  console.log(
    JSON.stringify(
      { ok: true, clicked, shot, media: await collectMedia(page, { sessionOnly: true }) },
      null,
      2
    )
  );
  process.exit(0);
}

if (MODE === "download") {
  const result = await downloadVideos(page);
  const shot = await snapshot(page, "download_state");
  console.log(JSON.stringify({ ok: result.saved.length > 0, ...result, shot }, null, 2));
  process.exit(result.saved.length ? 0 : 4);
}

if (MODE === "wait") {
  const maxMs = Number(process.env.GROK_WAIT_MS || 12 * 60 * 1000);
  const start = Date.now();
  let last = null;
  let baselineUuids = new Set();
  let baselineSet = false;

  // Prefer session marker from start
  const markerPath = path.join(OUT, "agent_session.json");
  let sessionUrl = null;
  if (fs.existsSync(markerPath)) {
    try {
      const m = JSON.parse(fs.readFileSync(markerPath, "utf8"));
      sessionUrl = m.url;
      if (m.keywords?.length) keywords = m.keywords;
    } catch {
      /* ignore */
    }
  }

  while (Date.now() - start < maxMs) {
    const paywall = await detectPaywall(page);
    if (paywall.blocked) {
      const shot = await snapshot(page, "wait_paywall");
      console.log(
        JSON.stringify({ ok: false, reason: "supergrok_paywall", paywall, shot, last }, null, 2)
      );
      process.exit(6);
    }

    const info = await pageInfo(page, keywords);
    if (!info.isAgentUrl) {
      last = {
        t: Math.round((Date.now() - start) / 1000),
        url: info.url,
        warn: "not_on_agent_url",
        title: info.title,
      };
      console.log(JSON.stringify(last));
      await page.waitForTimeout(10000);
      continue;
    }

    // Scroll lightly to load lazy videos in THIS canvas
    await page.mouse.wheel(0, 600).catch(() => {});
    await page.waitForTimeout(400);

    const media = await collectMedia(page, { sessionOnly: true });
    const sessionVideos = media.videos.filter((v) => !v.sidebar);
    const uuids = media.uniqueVideoUuids || [];
    const bigImgs = media.imgs.filter(
      (i) => !i.sidebar && i.nw >= 512 && (i.w >= 120 || /generated/i.test(i.alt))
    );

    if (!baselineSet) {
      // First poll: record what was already there (history leakage residual)
      baselineUuids = new Set(uuids);
      baselineSet = true;
    }
    const newUuids = uuids.filter((u) => !baselineUuids.has(u));
    // After 30s, treat all session UUIDs as candidates if we started clean
    const effectiveUuids =
      Date.now() - start > 45000 && uuids.length <= EXPECT_PANELS + 2
        ? uuids
        : newUuids.length
          ? newUuids
          : uuids;

    last = {
      t: Math.round((Date.now() - start) / 1000),
      url: info.url,
      title: info.title,
      isAgentUrl: info.isAgentUrl,
      hasBriefKeywords: info.hasBriefKeywords,
      keywordHits: info.keywordHits,
      sessionVideos: sessionVideos.length,
      uniqueVideoUuids: uuids.length,
      newUuidsSinceStart: newUuids.length,
      effectiveUuids: effectiveUuids.length,
      bigImgs: bigImgs.length,
      buttons: media.buttons,
      videoMeta: sessionVideos.slice(0, 12).map((v) => ({
        dur: v.dur,
        w: v.w,
        h: v.h,
        uuid: v.uuid?.slice(0, 12),
        src: v.src?.slice(0, 80),
      })),
      sessionUrl,
    };
    console.log(JSON.stringify(last));

    // Ready: enough unique session video UUIDs (not sidebar history of 65)
    if (effectiveUuids.length >= EXPECT_PANELS || uuids.length >= EXPECT_PANELS) {
      const shot = await snapshot(page, "wait_progress_ok");
      console.log(
        JSON.stringify(
          {
            ok: true,
            reason: "session_videos_ready",
            last,
            shot,
            uuids: effectiveUuids.length >= EXPECT_PANELS ? effectiveUuids : uuids,
          },
          null,
          2
        )
      );
      process.exit(0);
    }

    // Partial progress: ≥3 session videos with real host URLs
    if (
      uuids.length >= 3 &&
      sessionVideos.some((v) => /assets\.grok\.com.*generated/i.test(v.src)) &&
      Date.now() - start > 120000
    ) {
      // keep waiting until EXPECT or timeout — log only
    }

    // Stills-only ready path
    if (bigImgs.length >= EXPECT_PANELS && uuids.length === 0 && Date.now() - start > 90000) {
      const shot = await snapshot(page, "stills_ready");
      console.log(JSON.stringify({ ok: true, reason: "stills_ready", last, shot }, null, 2));
      process.exit(0);
    }

    await page.waitForTimeout(15000);
  }

  const shot = await snapshot(page, "wait_timeout");
  console.log(JSON.stringify({ ok: false, reason: "timeout", last, shot }, null, 2));
  process.exit(5);
}

console.error("Unknown mode", MODE);
process.exit(1);

/**
 * Harvest from open /imagine/post/{uuid} tabs OR navigate and wait.
 * Requires video src to include post uuid OR largest video on that post page only after stayed=======true.
 * Env: GROK_MANIFEST, GROK_OUT, GROK_WAIT_EACH_MS
 */
import { chromium } from "playwright-core";
import fs from "fs";
import path from "path";
import { spawnSync } from "child_process";

function requireEnv(name) {
  const v = (process.env[name] || "").trim();
  if (!v) {
    console.error(`Set ${name} to a local path. This script has no machine default.`);
    process.exit(2);
  }
  return v;
}

const FIRE = requireEnv("GROK_FIRE_DIR");
const MANIFEST = process.env.GROK_MANIFEST || path.join(FIRE, "fire_manifest.json");
const OUT = process.env.GROK_OUT || path.join(FIRE, "clips_wave2");
const FRAMES = path.join(OUT, "frames");
const CDP = process.env.GROK_CDP || "http://127.0.0.1:9222";
const WAIT_EACH = Number(process.env.GROK_WAIT_EACH_MS || "240000");

fs.mkdirSync(OUT, { recursive: true });
fs.mkdirSync(FRAMES, { recursive: true });

const manifest = JSON.parse(fs.readFileSync(MANIFEST, "utf8"));
const browser = await chromium.connectOverCDP(CDP);
const ctx = browser.contexts()[0];

function pageForUuid(uuid) {
  return ctx.pages().find((p) => p.url().includes(uuid));
}

async function collectOnPage(page, uuid) {
  return page.evaluate((want) => {
    const body = document.body?.innerText || "";
    const pct = body.match(/Generating\s+(\d{1,3})\s*%/i) || body.match(/(\d{1,3})\s*%/);
    const videos = [...document.querySelectorAll("video")]
      .map((v) => {
        const r = v.getBoundingClientRect();
        const src = v.currentSrc || v.src || "";
        return {
          src,
          w: v.videoWidth || 0,
          h: v.videoHeight || 0,
          display: Math.round(r.width * r.height),
          y: Math.round(r.top),
          matchPost: src.includes(want),
          hosted: /assets\.grok\.com|imagine-public|generated_video|\.mp4/i.test(src),
        };
      })
      .filter((v) => v.src)
      .sort((a, b) => b.display - a.display || (b.matchPost ? 1 : 0) - (a.matchPost ? 1 : 0));
    return {
      url: location.href,
      stayed: location.href.includes(want),
      progress: pct ? Number(pct[1]) : null,
      generating: /generat|queue|processing/i.test(body),
      videos,
      best: videos.find((v) => v.matchPost && v.hosted) || (videos[0]?.display > 20000 ? videos[0] : null),
    };
  }, uuid);
}

async function download(page, src, dest) {
  if (src.startsWith("blob:")) {
    const buf = await page.evaluate(async (s) => {
      const res = await fetch(s);
      const ab = await res.arrayBuffer();
      return Array.from(new Uint8Array(ab));
    }, src);
    fs.writeFileSync(dest, Buffer.from(buf));
    return;
  }
  const res = await page.request.get(src);
  if (!res.ok()) throw new Error(`http_${res.status()}`);
  fs.writeFileSync(dest, await res.body());
}

const results = [];
for (const shot of manifest.shots) {
  const dest = path.join(OUT, `${shot.id}.mp4`);
  const frame = path.join(FRAMES, `${shot.id}.jpg`);
  console.log("HARVEST", shot.id, shot.uuid);

  if (fs.existsSync(dest) && fs.statSync(dest).size > 80000) {
    if (!fs.existsSync(frame)) {
      spawnSync("ffmpeg", ["-y", "-ss", "2", "-i", dest, "-frames:v", "1", "-q:v", "3", frame], {
        encoding: "utf8",
      });
    }
    results.push({ id: shot.id, ok: true, skipped: true, bytes: fs.statSync(dest).size, frame });
    continue;
  }

  let page = pageForUuid(shot.uuid);
  if (!page) {
    page = await ctx.newPage();
    await page.goto(`https://grok.com/imagine/post/${shot.uuid}`, {
      waitUntil: "domcontentloaded",
      timeout: 90000,
    });
    await page.waitForTimeout(2500);
  } else {
    await page.bringToFront().catch(() => {});
  }

  const start = Date.now();
  let info = null;
  let ready = null;
  while (Date.now() - start < WAIT_EACH) {
    info = await collectOnPage(page, shot.uuid);
    if (!info.stayed) {
      results.push({ id: shot.id, ok: false, reason: "redirected_away", url: info.url });
      ready = null;
      break;
    }
    // Prefer completed large video; if matching post uuid in src even better
    const candidates = info.videos.filter(
      (v) => v.hosted && v.display >= 40000 && !/hero_product|agent-skills/i.test(v.src),
    );
    const pick =
      candidates.find((v) => v.matchPost) ||
      candidates[0] ||
      (info.best && info.best.display >= 40000 ? info.best : null);
    if (pick && pick.src && !info.generating) {
      ready = pick;
      break;
    }
    // If generating ended and video has dimensions
    if (pick && pick.w >= 640 && (!info.progress || info.progress >= 100)) {
      ready = pick;
      break;
    }
    await page.waitForTimeout(5000);
  }

  if (!ready?.src) {
    results.push({
      id: shot.id,
      ok: false,
      reason: "not_ready",
      progress: info?.progress ?? null,
      generating: info?.generating ?? null,
      stayed: info?.stayed ?? null,
      url: info?.url,
      videoCount: info?.videos?.length ?? 0,
    });
    continue;
  }

  try {
    await download(page, ready.src, dest);
  } catch (e) {
    results.push({ id: shot.id, ok: false, reason: "download_error", error: String(e).slice(0, 160) });
    continue;
  }
  const bytes = fs.statSync(dest).size;
  if (bytes < 50000) {
    results.push({ id: shot.id, ok: false, reason: "too_small", bytes });
    continue;
  }
  spawnSync("ffmpeg", ["-y", "-ss", "2", "-i", dest, "-frames:v", "1", "-q:v", "3", frame], {
    encoding: "utf8",
  });
  const row = {
    id: shot.id,
    ok: true,
    uuid: shot.uuid,
    file: dest,
    frame: fs.existsSync(frame) ? frame : null,
    bytes,
    src: ready.src.slice(0, 180),
    matchPost: ready.matchPost,
    w: ready.w,
    h: ready.h,
  };
  results.push(row);
  console.log("RESULT", JSON.stringify(row));
}

const report = {
  t: new Date().toISOString(),
  okCount: results.filter((r) => r.ok).length,
  failCount: results.filter((r) => !r.ok).length,
  results,
};
fs.writeFileSync(path.join(FIRE, "harvest_wave2_report.json"), JSON.stringify(report, null, 2));
console.log(JSON.stringify({ okCount: report.okCount, failCount: report.failCount }, null, 2));
process.exit(report.failCount ? 3 : 0);

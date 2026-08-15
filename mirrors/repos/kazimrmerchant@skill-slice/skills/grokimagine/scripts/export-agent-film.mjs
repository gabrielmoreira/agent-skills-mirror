/**
 * Proven Agent export: scroll canvas → unique video UUIDs → download MP4s
 * → optional first-pass concat (DOM order) → QC frame grabs → report JSON.
 *
 * Env:
 *   GROK_CDP   default http://127.0.0.1:9222
 *   GROK_OUT   export root (creates clips/, frames/)
 *   GROK_FINAL optional final filename (default FINAL_agent_export.mp4)
 *   GROK_CONCAT=0 to skip DOM-order concat
 */
import { chromium } from "playwright-core";
import fs from "fs";
import path from "path";
import { spawnSync } from "child_process";

const CDP = process.env.GROK_CDP || "http://127.0.0.1:9222";
const OUT = process.env.GROK_OUT || path.join(process.cwd(), "exports");
const FINAL_NAME = process.env.GROK_FINAL || "FINAL_agent_export.mp4";
const DO_CONCAT = process.env.GROK_CONCAT !== "0";

const CLIPS = path.join(OUT, "clips");
const FRAMES = path.join(OUT, "frames");
fs.mkdirSync(CLIPS, { recursive: true });
fs.mkdirSync(FRAMES, { recursive: true });

function idFromUrl(u) {
  const m = String(u || "").match(/generated\/([a-f0-9-]+)/i);
  return m ? m[1] : null;
}

function writeUtf8NoBom(file, text) {
  fs.writeFileSync(file, text, { encoding: "utf8" });
}

const browser = await chromium.connectOverCDP(CDP);
const context = browser.contexts()[0];
if (!context) {
  console.error(JSON.stringify({ ok: false, reason: "no_browser_context" }));
  process.exit(2);
}
const page =
  context.pages().find((p) => /imagine\/agent|grok\.com\/imagine/i.test(p.url())) ||
  context.pages()[0];
if (!page) {
  console.error(JSON.stringify({ ok: false, reason: "no_page" }));
  process.exit(2);
}

for (let i = 0; i < 8; i++) {
  await page.mouse.wheel(0, 900);
  await page.waitForTimeout(500);
}
for (let i = 0; i < 8; i++) {
  await page.mouse.wheel(0, -900);
  await page.waitForTimeout(350);
}
await page.waitForTimeout(1200);

const media = await page.evaluate(() => {
  return [...document.querySelectorAll("video")].map((v, idx) => {
    const r = v.getBoundingClientRect();
    return {
      idx,
      src: v.currentSrc || v.src || "",
      w: v.videoWidth,
      h: v.videoHeight,
      dur: Number.isFinite(v.duration) ? v.duration : 0,
      y: r.top + window.scrollY,
      x: r.left + window.scrollX,
    };
  });
});

const byId = new Map();
for (const v of media) {
  const id = idFromUrl(v.src);
  if (!id || !v.src || v.src.startsWith("blob:")) continue;
  if (!byId.has(id)) byId.set(id, v);
}
const unique = [...byId.values()].sort((a, b) => a.y - b.y || a.x - b.x);

const saved = [];
let n = 0;
for (const v of unique) {
  n += 1;
  const id = idFromUrl(v.src);
  const short = id.slice(0, 12);
  const file = path.join(CLIPS, `p${String(n).padStart(2, "0")}_${short}.mp4`);
  if (!fs.existsSync(file) || fs.statSync(file).size < 10000) {
    const res = await page.request.get(v.src);
    if (!res.ok()) {
      console.error("download_fail", id, res.status());
      continue;
    }
    fs.writeFileSync(file, await res.body());
  }
  const frame = path.join(FRAMES, `p${String(n).padStart(2, "0")}_${short}.jpg`);
  if (!fs.existsSync(frame)) {
    spawnSync(
      "ffmpeg",
      ["-y", "-ss", "1", "-i", file, "-frames:v", "1", "-q:v", "3", frame],
      { encoding: "utf8" }
    );
  }
  saved.push({
    n,
    id,
    file,
    frame: fs.existsSync(frame) ? frame : null,
    bytes: fs.statSync(file).size,
    dur: v.dur,
    w: v.w,
    h: v.h,
    y: v.y,
    x: v.x,
  });
}

// Best-effort UI export (often missing)
async function clickAny(names) {
  for (const name of names) {
    const btn = page.getByRole("button", { name: new RegExp(name, "i") });
    if (await btn.count()) {
      await btn.first().click({ force: true }).catch(() => {});
      return name;
    }
  }
  return null;
}
const stitchClick = await clickAny([
  "Stitch",
  "Export video",
  "Export",
  "Download video",
  "Download",
  "Compile",
  "Create video",
]);

let finalPath = null;
let finalSize = 0;
let ffmpegOk = false;
let ffmpegNote = "";
if (DO_CONCAT && saved.length >= 2) {
  const listPath = path.join(OUT, "concat_dom_order.txt");
  const lines = saved.map((s) => `file '${s.file.replace(/\\/g, "/")}'`).join("\n") + "\n";
  writeUtf8NoBom(listPath, lines);
  finalPath = path.join(OUT, FINAL_NAME);
  const r = spawnSync(
    "ffmpeg",
    ["-y", "-f", "concat", "-safe", "0", "-i", listPath, "-c", "copy", finalPath],
    { encoding: "utf8" }
  );
  ffmpegOk = r.status === 0 && fs.existsSync(finalPath);
  finalSize = ffmpegOk ? fs.statSync(finalPath).size : 0;
  ffmpegNote = (r.stderr || r.stdout || "").slice(-500);
}

const shot = path.join(OUT, `export_state_${Date.now()}.png`);
await page.screenshot({ path: shot, fullPage: false }).catch(() => {});

const report = {
  ok: saved.length > 0,
  url: page.url(),
  uniqueCount: saved.length,
  saved,
  stitchClick,
  domOrderWarning:
    "DOM y/x order is a first guess only. Open frames/ and re-stitch with stitch-story-order.mjs.",
  finalPath: ffmpegOk ? finalPath : null,
  finalSize,
  ffmpegOk,
  ffmpegNote,
  shot: fs.existsSync(shot) ? shot : null,
  next: [
    "Inspect frames/*.jpg and map each clip to a story beat",
    "Set GROK_ORDER=basename1.mp4,basename2.mp4,... under clips/",
    "Run stitch-story-order.mjs for FINAL story-order film",
  ],
};

fs.writeFileSync(path.join(OUT, "export_report.json"), JSON.stringify(report, null, 2));
console.log(JSON.stringify(report, null, 2));
process.exit(saved.length ? 0 : 4);

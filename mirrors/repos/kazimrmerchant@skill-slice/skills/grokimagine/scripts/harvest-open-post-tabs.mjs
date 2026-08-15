/**
 * Screenshot + download main video from each open /imagine/post/ tab.
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

const OUT = requireEnv("GROK_OUT");
fs.mkdirSync(OUT, { recursive: true });
fs.mkdirSync(path.join(OUT, "frames"), { recursive: true });

const browser = await chromium.connectOverCDP(process.env.GROK_CDP || "http://127.0.0.1:9222");
const ctx = browser.contexts()[0];
const posts = ctx.pages().filter((p) => /\/imagine\/post\//i.test(p.url()));
const seen = new Set();
const results = [];

for (const page of posts) {
  const m = page.url().match(/\/imagine\/post\/([a-f0-9-]+)/i);
  const uuid = m?.[1];
  if (!uuid || seen.has(uuid)) continue;
  seen.add(uuid);
  await page.bringToFront().catch(() => {});
  await page.waitForTimeout(1500);
  const shot = path.join(OUT, `${uuid.slice(0, 12)}.png`);
  await page.screenshot({ path: shot, fullPage: false }).catch(() => null);
  const info = await page.evaluate(() => {
    const body = (document.body?.innerText || "").slice(0, 400);
    const vids = [...document.querySelectorAll("video")]
      .map((v) => {
        const r = v.getBoundingClientRect();
        return {
          src: v.currentSrc || v.src || "",
          w: v.videoWidth,
          h: v.videoHeight,
          display: Math.round(r.width * r.height),
          y: Math.round(r.top),
        };
      })
      .filter((v) => v.src)
      .sort((a, b) => b.display - a.display);
    return { body, vids: vids.slice(0, 5) };
  });
  const main = info.vids.find((v) => v.display > 80000) || info.vids[0];
  let file = null;
  let frame = null;
  if (main?.src && !main.src.startsWith("blob:") && /assets\.grok|generated|\.mp4/i.test(main.src)) {
    file = path.join(OUT, `${uuid.slice(0, 12)}.mp4`);
    const res = await page.request.get(main.src);
    if (res.ok()) {
      fs.writeFileSync(file, await res.body());
      frame = path.join(OUT, "frames", `${uuid.slice(0, 12)}.jpg`);
      spawnSync("ffmpeg", ["-y", "-ss", "2", "-i", file, "-frames:v", "1", "-q:v", "3", frame], {
        encoding: "utf8",
      });
    }
  }
  results.push({
    uuid,
    url: page.url().slice(0, 120),
    shot,
    file,
    frame: frame && fs.existsSync(frame) ? frame : null,
    bytes: file && fs.existsSync(file) ? fs.statSync(file).size : 0,
    mainDisplay: main?.display,
    mainSrc: main?.src?.slice(0, 160),
    bodyHead: info.body.slice(0, 120),
  });
  console.log(JSON.stringify(results[results.length - 1]));
}

fs.writeFileSync(path.join(OUT, "report.json"), JSON.stringify(results, null, 2));
console.log("DONE", results.length);
process.exit(0);

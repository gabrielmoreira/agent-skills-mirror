/**
 * Download all unique Grok agent videos + large images from current page.
 */
import { chromium } from "playwright-core";
import fs from "fs";
import path from "path";
import crypto from "crypto";

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
const PREFIX = process.env.GROK_PREFIX || "clip";

fs.mkdirSync(OUT, { recursive: true });

function idFromUrl(u) {
  const m = u.match(/generated\/([a-f0-9-]+)/i);
  return m ? m[1].slice(0, 12) : crypto.createHash("md5").update(u).digest("hex").slice(0, 12);
}

const browser = await chromium.connectOverCDP(CDP);
const context = browser.contexts()[0];
const page =
  context.pages().find((p) => /imagine\/agent/i.test(p.url())) ||
  context.pages()[0];

const media = await page.evaluate(() => {
  const videos = [...document.querySelectorAll("video")]
    .map((v) => ({
      src: v.currentSrc || v.src || "",
      w: v.videoWidth,
      h: v.videoHeight,
      dur: v.duration || 0,
    }))
    .filter((v) => v.src && !v.src.startsWith("blob:"));
  const imgs = [...document.querySelectorAll("img")]
    .map((i) => ({
      src: i.currentSrc || i.src || "",
      alt: i.alt || "",
      nw: i.naturalWidth,
      nh: i.naturalHeight,
    }))
    .filter((i) => i.nw >= 512 && i.src && !i.src.startsWith("data:"));
  return { videos, imgs };
});

const seenV = new Set();
const savedVideos = [];
for (const v of media.videos) {
  const key = idFromUrl(v.src);
  if (seenV.has(key)) continue;
  seenV.add(key);
  try {
    const res = await page.request.get(v.src);
    if (!res.ok()) continue;
    const f = path.join(OUT, `${PREFIX}_${String(savedVideos.length + 1).padStart(2, "0")}_${key}.mp4`);
    fs.writeFileSync(f, await res.body());
    savedVideos.push({ file: f, ...v, key });
  } catch (e) {
    console.error("video fail", key, e.message);
  }
}

const seenI = new Set();
const savedImgs = [];
for (const img of media.imgs) {
  const key = idFromUrl(img.src) || crypto.createHash("md5").update(img.src).digest("hex").slice(0, 12);
  if (seenI.has(key)) continue;
  seenI.add(key);
  try {
    const res = await page.request.get(img.src);
    if (!res.ok()) continue;
    const ext = /webp/i.test(img.src) ? "webp" : /png/i.test(img.src) ? "png" : "jpg";
    const f = path.join(OUT, `still_${String(savedImgs.length + 1).padStart(2, "0")}_${key}.${ext}`);
    fs.writeFileSync(f, await res.body());
    savedImgs.push({ file: f, nw: img.nw, nh: img.nh, key });
  } catch {}
}

// Also capture data: images
const dataImgs = await page.evaluate(() =>
  [...document.querySelectorAll('img[alt*="Generated" i], img')]
    .filter((i) => (i.src || "").startsWith("data:image") && i.naturalWidth >= 512)
    .map((i) => ({ src: i.src, nw: i.naturalWidth, nh: i.naturalHeight, alt: i.alt || "" }))
);
for (const img of dataImgs) {
  const key = crypto.createHash("md5").update(img.src.slice(0, 2000)).digest("hex").slice(0, 12);
  if (seenI.has(key)) continue;
  seenI.add(key);
  const m = img.src.match(/^data:image\/(\w+);base64,(.+)$/);
  if (!m) continue;
  const f = path.join(OUT, `still_data_${String(savedImgs.length + 1).padStart(2, "0")}_${key}.${m[1] === "jpeg" ? "jpg" : m[1]}`);
  fs.writeFileSync(f, Buffer.from(m[2], "base64"));
  savedImgs.push({ file: f, nw: img.nw, nh: img.nh, key });
}

console.log(
  JSON.stringify(
    {
      url: page.url(),
      savedVideos,
      savedImgsCount: savedImgs.length,
      savedImgs: savedImgs.map((i) => i.file),
    },
    null,
    2
  )
);

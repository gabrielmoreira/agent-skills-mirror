#!/usr/bin/env node
// MediaPipe twin of faces.swift and matte.swift, for Windows and any machine without Apple Vision: same command line,
// same output files, computed in headless Chrome (playwright-core + @mediapipe/tasks-vision on the CPU, models fetched once).
//   node vision-web.mjs faces <camDir> <out.json>             [[cx, cy, w, h, roll], ...] per frame, gaps filled, smoothed
//   node vision-web.mjs matte <camDir> <outDir> <jobFile>     job lines "<frame> <rawMaskPath> <write 0|1>" (see matte.swift)
//   node vision-web.mjs fetch                                 download the models now (the installer does, so edits work offline)
// platform.mjs picks this path when Apple Vision is not there (SHORT_EDITING_VISION=web forces it, to compare on a Mac).
import fs from 'node:fs';
import path from 'node:path';
import { createRequire } from 'node:module';
import { ENGINE, CHROME, RUNTIME, CACHE } from './platform.mjs';

const MODELS = {
  faces: ['blaze_face_short_range.tflite', 'https://storage.googleapis.com/mediapipe-models/face_detector/blaze_face_short_range/float16/1/blaze_face_short_range.tflite'],
  matte: ['selfie_multiclass_256x256.tflite', 'https://storage.googleapis.com/mediapipe-models/image_segmenter/selfie_multiclass_256x256/float32/1/selfie_multiclass_256x256.tflite'],
};
const MODEL_DIR = path.join(RUNTIME || CACHE, 'models');

async function model(k) {
  const [name, url] = MODELS[k], f = path.join(MODEL_DIR, name);
  if (fs.existsSync(f)) return f;
  fs.mkdirSync(MODEL_DIR, { recursive: true });
  const r = await fetch(url);
  if (!r.ok) throw new Error(`model download failed (${r.status}): ${url}`);
  fs.writeFileSync(f + '.tmp', Buffer.from(await r.arrayBuffer())); fs.renameSync(f + '.tmp', f);
  return f;
}

// Everything the page reads or writes goes through one fake origin: /mp/* = the tasks-vision package, /file?f= reads a
// local file, POST /put?f= writes one. No server, no port.
const TYPES = { '.mjs': 'text/javascript', '.js': 'text/javascript', '.wasm': 'application/wasm', '.jpg': 'image/jpeg', '.png': 'image/png', '.tflite': 'application/octet-stream' };
const PAGE = `<!doctype html><script type="module">import * as V from '/mp/vision_bundle.mjs'; window.V = V; window.READY = true;</script>`;
async function withPage(fn) {
  const { chromium } = createRequire(path.join(ENGINE, 'package.json'))('playwright-core');
  const MP = path.dirname(createRequire(path.join(ENGINE, 'package.json')).resolve('@mediapipe/tasks-vision'));
  const browser = await chromium.launch({ executablePath: CHROME, headless: true, args: ['--disable-extensions', '--mute-audio'] });
  try {
    const page = await browser.newPage();
    page.on('pageerror', e => console.error('  pageerror:', e.message));
    await page.route('http://vision.local/**', async route => {
      const u = new URL(route.request().url()), f = u.searchParams.get('f');
      if (u.pathname === '/') return route.fulfill({ body: PAGE, contentType: 'text/html' });
      if (u.pathname === '/put') { const t = f + '.tmp'; fs.writeFileSync(t, route.request().postDataBuffer()); fs.renameSync(t, f); return route.fulfill({ body: 'ok' }); }
      const file = u.pathname === '/file' ? f : u.pathname.startsWith('/mp/') ? path.join(MP, decodeURIComponent(u.pathname.slice(4))) : null;
      if (!file || !fs.existsSync(file)) return route.fulfill({ status: 404, body: 'not found' });
      return route.fulfill({ body: fs.readFileSync(file), contentType: TYPES[path.extname(file)] || 'application/octet-stream' });
    });
    await page.goto('http://vision.local/');
    await page.waitForFunction(() => window.READY === true, null, { timeout: 60000 });
    return await fn(page);
  } finally { await browser.close(); }
}
const fileURL = f => 'http://vision.local/file?f=' + encodeURIComponent(f);

// ---- faces: the widest face per frame in frame px (y down), roll in radians (clockwise on screen)
async function faces(dir, out) {
  const m = await model('faces'), files = fs.readdirSync(dir).filter(f => f.endsWith('.jpg')).sort();
  const raw = await withPage(async page => {
    await page.evaluate(async m => {
      const fset = await V.FilesetResolver.forVisionTasks('/mp/wasm');
      window.det = await V.FaceDetector.createFromOptions(fset, { baseOptions: { modelAssetPath: m, delegate: 'CPU' }, runningMode: 'IMAGE', minDetectionConfidence: .5 });
    }, fileURL(m));
    const res = [];
    for (const [i, f] of files.entries()) {
      res.push(await page.evaluate(async url => {
        const img = await createImageBitmap(await (await fetch(url)).blob()), W = img.width, H = img.height;
        const best = det.detect(img).detections.sort((a, b) => b.boundingBox.width - a.boundingBox.width)[0];
        img.close();
        if (!best) return null;
        const b = best.boundingBox, [r, l] = best.keypoints;   // the subject's right eye (image left), then left eye
        // BlazeFace boxes run ~15% larger and a bit lower than Apple Vision's: scale them to the same face box
        const k = .86, w = b.width * k, h = b.height * k;
        return [b.originX + b.width / 2, b.originY + b.height / 2 - .03 * b.height, w, h, r && l ? Math.atan2((l.y - r.y) * H, (l.x - r.x) * W) : 0];
      }, fileURL(path.join(dir, f))));
      if (i % 200 === 0) console.log(`faces ${i + 1}/${files.length}`);
    }
    return res;
  });
  // fill gaps from the last detection (the first one before it), then a centred moving average, radius 3 frames
  let last = raw.find(Boolean) || null;
  const filled = raw.map(v => (last = v || last));
  const outRows = filled.map((_, i) => {
    const acc = [0, 0, 0, 0, 0]; let n = 0;
    for (let j = Math.max(0, i - 3); j <= Math.min(filled.length - 1, i + 3); j++) if (filled[j]) { filled[j].forEach((x, k) => acc[k] += x); n++; }
    return n ? acc.map(x => Math.round(x / n * 10) / 10) : [0, 0, 0, 0, 0];
  });
  fs.writeFileSync(out, JSON.stringify(outRows));
  console.log(`faces done: ${outRows.length} frames, ${raw.filter(Boolean).length} detected`);
}

// ---- matte: person = 1 - background confidence, upscaled to the cam frame, cached as a gray PNG; then a temporal EMA
// (40% previous) and a 5x5 gaussian, written as <outDir>/%05d.png with alpha = person (rgb 0), like matte.swift
async function matte(camDir, outDir, jobFile) {
  const m = await model('matte');
  fs.mkdirSync(outDir, { recursive: true });
  const jobs = fs.readFileSync(jobFile, 'utf8').split('\n').map(l => l.trim().split(' ')).filter(f => f.length === 3 && /^\d+$/.test(f[0]));
  await withPage(async page => {
    await page.evaluate(async m => {
      const fset = await V.FilesetResolver.forVisionTasks('/mp/wasm');
      window.seg = await V.ImageSegmenter.createFromOptions(fset, { baseOptions: { modelAssetPath: m, delegate: 'CPU' }, runningMode: 'IMAGE', outputConfidenceMasks: true, outputCategoryMask: false });
      const G = [0.0398, 0.2420, 0.4364, 0.2420, 0.0398];
      const png = async (c, put) => fetch(put, { method: 'POST', body: await c.convertToBlob({ type: 'image/png' }) });
      let ema = null, tmp = null, prev = -2;
      window.matteFrame = async ({ i, cam, cache, cached, cachePut, outPut, write }) => {
        let W, H, raw;
        if (cached) {
          const bm = await createImageBitmap(await (await fetch(cache)).blob()); W = bm.width; H = bm.height;
          const c = new OffscreenCanvas(W, H), x = c.getContext('2d'); x.drawImage(bm, 0, 0); bm.close();
          const d = x.getImageData(0, 0, W, H).data; raw = new Uint8Array(W * H); for (let j = 0; j < W * H; j++) raw[j] = d[4 * j];
        } else {
          const img = await createImageBitmap(await (await fetch(cam)).blob()); W = img.width; H = img.height;
          const r = seg.segment(img), bg = r.confidenceMasks[0], mw = bg.width, mh = bg.height, p = bg.getAsFloat32Array();
          // person = 1 - background, 0.3..0.7 stretched to 0..1 (no grey haze in the background)
          const small = new OffscreenCanvas(mw, mh), sx = small.getContext('2d'), id = sx.createImageData(mw, mh);
          for (let j = 0; j < mw * mh; j++) { const v = Math.round(Math.min(1, Math.max(0, (.7 - p[j]) / .4)) * 255); id.data[4 * j] = id.data[4 * j + 1] = id.data[4 * j + 2] = v; id.data[4 * j + 3] = 255; }
          sx.putImageData(id, 0, 0); r.close(); img.close();
          const c = new OffscreenCanvas(W, H), x = c.getContext('2d'); x.imageSmoothingQuality = 'high'; x.drawImage(small, 0, 0, W, H);
          const d = x.getImageData(0, 0, W, H).data; raw = new Uint8Array(W * H); for (let j = 0; j < W * H; j++) raw[j] = d[4 * j];
          await png(c, cachePut);
        }
        if (!ema || ema.length !== W * H || i !== prev + 1) { ema = Float32Array.from(raw); tmp = new Float32Array(W * H); }
        else for (let j = 0; j < W * H; j++) ema[j] += .6 * (raw[j] - ema[j]);
        prev = i;
        if (!write) return;
        // separable 5x5 gaussian, edges extended; alpha = mask, rgb 0
        for (let y = 0; y < H; y++) for (let x = 0; x < W; x++) {
          let s = 0; for (let k = -2; k <= 2; k++) s += G[k + 2] * Math.floor(ema[y * W + Math.min(W - 1, Math.max(0, x + k))]);
          tmp[y * W + x] = s;
        }
        const c = new OffscreenCanvas(W, H), x = c.getContext('2d'), id = x.createImageData(W, H);
        for (let y = 0; y < H; y++) for (let xx = 0; xx < W; xx++) {
          let s = 0; for (let k = -2; k <= 2; k++) s += G[k + 2] * tmp[Math.min(H - 1, Math.max(0, y + k)) * W + xx];
          id.data[4 * (y * W + xx) + 3] = Math.min(255, Math.round(s));
        }
        x.putImageData(id, 0, 0);
        await png(c, outPut);
      };
    }, fileURL(m));
    let written = 0;
    for (const [i, rawPath, w] of jobs) {
      const name = String(+i).padStart(5, '0');
      await page.evaluate(a => window.matteFrame(a), {
        i: +i, cam: fileURL(path.join(camDir, name + '.jpg')), cache: fileURL(rawPath), cached: fs.existsSync(rawPath),
        cachePut: 'http://vision.local/put?f=' + encodeURIComponent(rawPath), outPut: 'http://vision.local/put?f=' + encodeURIComponent(path.join(outDir, name + '.png')), write: w === '1',
      });
      if (w === '1' && ++written % 10 === 0) console.log(`matte ${written}`);
    }
  });
  console.log('matte done');
}

const [cmd, ...a] = process.argv.slice(2);
try {
  if (cmd === 'faces' && a.length === 2) await faces(...a);
  else if (cmd === 'matte' && a.length === 3) await matte(...a);
  else if (cmd === 'fetch') { for (const k of Object.keys(MODELS)) console.log(await model(k)); }
  else { console.log('usage: node vision-web.mjs faces <camDir> <out.json> | matte <camDir> <outDir> <jobFile> | fetch'); process.exit(1); }
} catch (e) { console.error(e.message); process.exit(1); }

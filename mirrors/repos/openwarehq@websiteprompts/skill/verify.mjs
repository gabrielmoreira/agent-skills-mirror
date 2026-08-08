#!/usr/bin/env node
// Headless render-verification harness for cinematic sites.
// Usage:
//   node verify.mjs <port> <name> [--webgl] [--scroll]
// Drives Chrome-for-Testing from ~/.cache/puppeteer (install puppeteer-core into a
// scratch dir if needed: `npm i puppeteer-core@23`). Screenshots the hero (+ a
// scrolled shot with --scroll), reports console/page errors and canvas/WebGL state.
// ALWAYS open the PNGs and look — a blank canvas + "200 OK" is NOT success.
import fs from 'fs';
import os from 'os';
import path from 'path';
import puppeteer from 'puppeteer-core';

const [port, name] = process.argv.slice(2);
const WEBGL = process.argv.includes('--webgl');
const SCROLL = process.argv.includes('--scroll');
if (!port || !name) { console.error('usage: node verify.mjs <port> <name> [--webgl] [--scroll]'); process.exit(1); }

// find the Chrome-for-Testing binary puppeteer downloaded
function findChrome() {
  const base = path.join(os.homedir(), '.cache/puppeteer/chrome');
  for (const d of fs.existsSync(base) ? fs.readdirSync(base) : []) {
    const mac = path.join(base, d);
    for (const sub of fs.readdirSync(mac)) {
      const app = path.join(mac, sub);
      const bins = [
        path.join(app, 'Google Chrome for Testing.app/Contents/MacOS/Google Chrome for Testing'),
        path.join(app, 'chrome'),
      ];
      for (const b of bins) if (fs.existsSync(b)) return b;
    }
  }
  return '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
}

const args = ['--no-sandbox'];
if (WEBGL) args.push('--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist', '--enable-webgl');

const outDir = process.env.SHOT_DIR || '/tmp';
fs.mkdirSync(outDir, { recursive: true }); // auto-create SHOT_DIR (matches capture-stops.mjs)
const browser = await puppeteer.launch({ executablePath: findChrome(), headless: true, args });
const page = await browser.newPage();
page.on('dialog', async d => { try { await d.dismiss(); } catch {} }); // some sites alert() on load
await page.setViewport({ width: 1512, height: 860, deviceScaleFactor: 1 });
const errs = [];
page.on('pageerror', e => errs.push(e.message));
page.on('console', m => { if (m.type() === 'error') errs.push('C:' + m.text().slice(0, 140)); });

await page.goto(`http://localhost:${port}/`, { waitUntil: 'networkidle2', timeout: 40000 });
if (WEBGL) await page.waitForSelector('canvas', { timeout: 15000 }).catch(() => errs.push('NO CANVAS'));
await new Promise(r => setTimeout(r, WEBGL ? 8000 : 2000)); // 3D needs warm-up

const info = await page.evaluate(() => {
  const c = document.querySelector('canvas');
  return { canvas: !!c, gl: c ? !!(c.getContext('webgl2') || c.getContext('webgl')) : false,
           w: c?.width, h: c?.height };
});
await page.screenshot({ path: path.join(outDir, `${name}-hero.png`) });

if (SCROLL) {
  // realistic scroll cadence (fast synthetic jumps give false "stuck reveal" positives)
  await page.evaluate(async () => {
    const h = document.body.scrollHeight;
    for (let y = 0; y <= h * 0.55; y += 90) { window.scrollTo(0, y); await new Promise(r => setTimeout(r, 110)); }
  });
  // also nudge any drei ScrollControls container
  await page.evaluate(() => {
    const el = [...document.querySelectorAll('div')].find(d => { const s = getComputedStyle(d); return (s.overflowY==='auto'||s.overflowY==='scroll') && d.scrollHeight > d.clientHeight + 50; });
    if (el) el.scrollTop = el.scrollHeight * 0.45;
  });
  await new Promise(r => setTimeout(r, 2200));
  await page.screenshot({ path: path.join(outDir, `${name}-mid.png`) });
}

console.log(`${name}: ${JSON.stringify(info)} | errors: ${errs.length ? JSON.stringify([...new Set(errs)].slice(0, 6)) : 'none'}`);
console.log(`shots: ${path.join(outDir, name + '-hero.png')}${SCROLL ? ' , -mid.png' : ''}`);
await browser.close();

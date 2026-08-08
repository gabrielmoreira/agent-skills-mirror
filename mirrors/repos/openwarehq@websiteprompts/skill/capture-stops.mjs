#!/usr/bin/env node
// Multi-stop scroll capture for scroll-choreographed sites (3D timelines,
// long motion runways). Screenshots the page at several scroll fractions so
// you can VERIFY every beat of an authored animation, not just the hero.
//
// Usage:
//   SHOT_DIR=/path node capture-stops.mjs <port> <name> [stops] [--warmup ms]
//   stops = comma list of 0..1 scroll fractions (default "0,0.2,0.4,0.6,0.8,0.95")
//
// Notes (hard-won):
// - goto uses domcontentloaded, NOT networkidle2 — big GLBs stream forever.
// - default warmup 12000ms covers GLB parse + intro animations; 2D sites can
//   pass --warmup 4000.
// - waits 2.6s after each jump so damped cameras settle.
// - ALWAYS open the PNGs and look.
import fs from 'fs';
import os from 'os';
import path from 'path';
import puppeteer from 'puppeteer-core';

const args = process.argv.slice(2).filter((a) => !a.startsWith('--'));
const [port, name, stopsArg] = args;
if (!port || !name) {
  console.error('usage: SHOT_DIR=... node capture-stops.mjs <port> <name> [stops] [--warmup ms]');
  process.exit(1);
}
const stops = (stopsArg || '0,0.2,0.4,0.6,0.8,0.95').split(',').map(Number);
const warmupIdx = process.argv.indexOf('--warmup');
const warmup = warmupIdx > -1 ? Number(process.argv[warmupIdx + 1]) : 12000;

function findChrome() {
  const base = path.join(os.homedir(), '.cache/puppeteer/chrome');
  for (const d of fs.existsSync(base) ? fs.readdirSync(base) : []) {
    const app = path.join(base, d);
    for (const sub of fs.readdirSync(app)) {
      const bins = [
        path.join(app, sub, 'Google Chrome for Testing.app/Contents/MacOS/Google Chrome for Testing'),
        path.join(app, sub, 'chrome'),
      ];
      for (const b of bins) if (fs.existsSync(b)) return b;
    }
  }
  return '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
}

const out = process.env.SHOT_DIR || '/tmp';
fs.mkdirSync(out, { recursive: true });
const browser = await puppeteer.launch({
  executablePath: findChrome(),
  headless: true,
  args: ['--no-sandbox', '--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist', '--enable-webgl'],
});
const page = await browser.newPage();
await page.setViewport({ width: 1512, height: 860, deviceScaleFactor: 1 });
const errs = [];
page.on('pageerror', (e) => errs.push(e.message));
page.on('console', (m) => { if (m.type() === 'error') errs.push('C:' + m.text().slice(0, 120)); });

await page.goto(`http://localhost:${port}/`, { waitUntil: 'domcontentloaded', timeout: 60000 });
await page.waitForSelector('canvas', { timeout: 20000 }).catch(() => {});
await new Promise((r) => setTimeout(r, warmup));

for (const p of stops) {
  await page.evaluate((prog) => {
    const max = document.documentElement.scrollHeight - window.innerHeight;
    window.scrollTo(0, max * prog);
  }, p);
  await new Promise((r) => setTimeout(r, 2600));
  const label = `${name}-${String(Math.round(p * 100)).padStart(2, '0')}`;
  await page.screenshot({ path: path.join(out, `${label}.png`) });
  console.log('shot', label);
}
console.log('errors:', JSON.stringify(errs.slice(0, 6)));
await browser.close();

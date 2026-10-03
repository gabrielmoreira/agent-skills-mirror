#!/usr/bin/env node
// Visual QA: screenshots in light/dark on phone/desktop, plus automatic layout checks.
//
//   node visual-check.mjs --base http://localhost:4400 --paths "/,/events/" --out shots \
//        [--clock 2026-10-01T22:00:00-04:00] [--full] [--no-shots]
//
// For each page: screenshots (phone 390 px @2x, desktop 1280 px; light + dark), horizontal overflow at
// 320 px (lists offending elements), header height across widths (detects wrapped navigation), console
// errors, failed images, and images shown larger than their natural size (upscaled).
// Run from a folder where Playwright is installed (the site repo). Exit code 1 if any check fails.
import { mkdirSync } from 'node:fs';
import { join } from 'node:path';
import { createRequire } from 'node:module';

const require = createRequire(join(process.cwd(), 'package.json'));
let pw;
try {
  pw = require('@playwright/test');
} catch {
  pw = require('playwright');
}
const { chromium, devices } = pw;
const args = process.argv.slice(2);
const get = (k, d) => {
  const i = args.indexOf(`--${k}`);
  return i >= 0 ? args[i + 1] : d;
};
const base = (get('base') || '').replace(/\/$/, '');
if (!base) {
  console.error('Usage: node visual-check.mjs --base http://localhost:4400 --paths "/,/events/" --out shots');
  process.exit(1);
}
const paths = (get('paths', '/') || '/').split(',').map((p) => p.trim()).filter(Boolean);
const out = get('out', 'shots');
const clock = get('clock');
const full = args.includes('--full');
const shots = !args.includes('--no-shots');
const headerSel = get('header', 'header, .site-header');
mkdirSync(out, { recursive: true });
const slug = (p) => (p === '/' ? 'home' : p.replace(/^\/|\/$/g, '').replace(/[^a-z0-9]+/gi, '-').toLowerCase());
let failures = 0;
const fail = (msg) => {
  failures++;
  console.log(`  ✗ ${msg}`);
};

const browser = await chromium.launch();
const newPage = async (opts) => {
  const ctx = await browser.newContext(opts);
  const page = await ctx.newPage();
  if (clock) await page.clock.setFixedTime(new Date(clock));
  const errors = [];
  page.on('console', (m) => m.type() === 'error' && errors.push(m.text()));
  page.on('pageerror', (e) => errors.push(String(e)));
  return { ctx, page, errors };
};
const open = async (page, url) => {
  try {
    await page.goto(url, { waitUntil: 'networkidle', timeout: 45000 });
  } catch {
    await page.goto(url, { waitUntil: 'load', timeout: 45000 });
  }
};

for (const p of paths) {
  console.log(`\n${p}`);
  // 1) Screenshots + console errors + images.
  for (const scheme of ['light', 'dark']) {
    for (const [label, opts] of [
      ['phone', { ...devices['iPhone 13'], deviceScaleFactor: 2 }],
      ['desktop', { viewport: { width: 1280, height: 900 } }],
    ]) {
      const { ctx, page, errors } = await newPage({ ...opts, colorScheme: scheme });
      await open(page, base + p);
      await page.evaluate(async () => {
        for (let y = 0; y < document.body.scrollHeight; y += innerHeight) {
          scrollTo(0, y);
          await new Promise((r) => setTimeout(r, 120));
        }
        scrollTo(0, 0);
      });
      await page.waitForTimeout(300);
      const img = await page.evaluate(async () => {
        const fileWidth = (src) =>
          new Promise((res) => {
            const im = new Image();
            im.onload = () => res(im.naturalWidth);
            im.onerror = () => res(0);
            im.src = src;
          });
        const list = [...document.images].filter((i) => i.getBoundingClientRect().width > 0 && !i.closest('[hidden], [aria-hidden="true"]'));
        const out = [];
        for (const i of list) {
          const src = i.currentSrc || i.src;
          const loaded = i.complete && i.naturalWidth > 0;
          out.push({
            src,
            // complete + no pixels = really broken; lazy images that have not started loading are skipped.
            broken: i.complete && i.naturalWidth === 0 && Boolean(src),
            loaded,
            // Blurred backdrops are tiny on purpose.
            decorative: /blur/.test(getComputedStyle(i).filter) || (i.alt === '' && /absolute|fixed/.test(getComputedStyle(i).position)),
            shown: i.getBoundingClientRect().width,
            // naturalWidth is density-adjusted for srcset images; load the chosen file alone to get its real pixel width.
            file: loaded ? await fileWidth(src) : 0,
          });
        }
        return out;
      });
      for (const i of img.filter((x) => x.broken)) fail(`${label}/${scheme}: image failed to load ${i.src}`);
      for (const i of img.filter((x) => x.loaded && !x.decorative && x.file && x.shown > x.file * 1.15)) {
        console.log(`  ! ${label}/${scheme}: image shown ${Math.round(i.shown)}px wide but the file is only ${i.file}px (upscaled, looks blurry): ${i.src.slice(0, 100)}`);
      }
      for (const e of errors) fail(`${label}/${scheme}: console error: ${e.slice(0, 160)}`);
      if (shots) {
        const file = join(out, `${slug(p)}-${label}-${scheme}.png`);
        await page.screenshot({ path: file, fullPage: full });
        console.log(`  · ${file}`);
      }
      await ctx.close();
    }
  }
  // 2) 320 px overflow.
  {
    const { ctx, page } = await newPage({ viewport: { width: 320, height: 640 } });
    await open(page, base + p);
    const r = await page.evaluate(() => {
      const W = document.documentElement.clientWidth;
      const offenders = [];
      for (const el of document.querySelectorAll('body *')) {
        const rc = el.getBoundingClientRect();
        if (rc.width > 0 && rc.right > W + 1 && !el.closest('[hidden], [aria-hidden="true"], .leaflet-container')) {
          offenders.push(`${el.tagName.toLowerCase()}${el.className && typeof el.className === 'string' ? '.' + el.className.trim().split(/\s+/).join('.') : ''} right=${Math.round(rc.right)}`);
        }
      }
      return { W, sw: document.documentElement.scrollWidth, offenders: offenders.slice(0, 6) };
    });
    if (r.sw > r.W + 1) fail(`320px: page scrolls sideways (${r.sw} > ${r.W}): ${r.offenders.join(' | ')}`);
    else console.log('  ✓ 320px: no sideways scrolling');
    await ctx.close();
  }
  // 3) Header height across widths (a jump = nav wrapped to two lines).
  {
    const heights = [];
    for (const w of [320, 390, 480, 768, 1024, 1120, 1280, 1366, 1600]) {
      const { ctx, page } = await newPage({ viewport: { width: w, height: 800 } });
      await open(page, base + p);
      const h = await page.evaluate((sel) => Math.round(document.querySelector(sel)?.getBoundingClientRect().height ?? 0), headerSel);
      heights.push([w, h]);
      await ctx.close();
    }
    const min = Math.min(...heights.map(([, h]) => h).filter(Boolean));
    const tall = heights.filter(([, h]) => h > min * 1.25);
    if (tall.length) fail(`header taller at ${tall.map(([w, h]) => `${w}px=${h}`).join(', ')} (min ${min}px): navigation probably wraps`);
    else console.log(`  ✓ header stays one row (${min}px) from 320 to 1600 px`);
  }
}
await browser.close();
console.log(`\n${failures ? `${failures} problem(s) found` : 'All automatic checks passed'}. Now LOOK at the screenshots in ${out}.`);
process.exit(failures ? 1 : 0);

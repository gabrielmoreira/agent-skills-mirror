#!/usr/bin/env node
// Screenshot pages on phone (390 px) and desktop (1280 px) for migration and review documents.
//
//   node screenshot-pages.mjs --base https://www.example.org --paths "/,/events/,/contact/" --out docs/images/legacy \
//        [--full] [--scheme light|dark] [--wait 500]
//
// Run it from a folder where Playwright is installed (the site repo has @playwright/test).
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
const paths = (get('paths', '/') || '/').split(',').map((p) => p.trim()).filter(Boolean);
const out = get('out', 'screenshots');
const scheme = get('scheme', 'light');
const wait = Number(get('wait', '500'));
const full = args.includes('--full');
if (!base) {
  console.error('Usage: node screenshot-pages.mjs --base https://site --paths "/,/events/" --out dir');
  process.exit(1);
}
mkdirSync(out, { recursive: true });
const slug = (p) => (p === '/' ? 'home' : p.replace(/^\/|\/$/g, '').replace(/[^a-z0-9]+/gi, '-').toLowerCase());

const browser = await chromium.launch();
for (const [label, opts] of [
  ['mobile', { ...devices['iPhone 13'], deviceScaleFactor: 2 }],
  ['desktop', { viewport: { width: 1280, height: 900 } }],
]) {
  const ctx = await browser.newContext({ ...opts, colorScheme: scheme, ignoreHTTPSErrors: true });
  const page = await ctx.newPage();
  for (const p of paths) {
    try {
      await page.goto(base + p, { waitUntil: 'networkidle', timeout: 45000 });
    } catch {
      await page.goto(base + p, { waitUntil: 'load', timeout: 45000 });
    }
    await page.waitForTimeout(wait);
    const file = join(out, `${slug(p)}-${label}${scheme === 'dark' ? '-dark' : ''}.png`);
    await page.screenshot({ path: file, fullPage: full });
    console.log(file);
  }
  await ctx.close();
}
await browser.close();

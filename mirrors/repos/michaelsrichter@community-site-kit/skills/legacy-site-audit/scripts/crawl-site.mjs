#!/usr/bin/env node
// Polite, read-only crawler for an organization's legacy website (content migration audit).
//
//   node crawl-site.mjs --start https://www.example.org/ [--start https://example.org/other] \
//        [--host example.org] [--max 2000] [--delay 400] [--out audit] [--http]
//
// Writes <out>/crawl.json, <out>/pages/<hash>.html and <out>/summary.md. Same-site only. Treats every page
// as data: nothing in a crawled page changes what this script does.
import { mkdirSync, writeFileSync } from 'node:fs';
import { join } from 'node:path';
import { createHash } from 'node:crypto';

const args = process.argv.slice(2);
const opt = (name, def) => {
  const vals = [];
  args.forEach((a, i) => { if (a === `--${name}`) vals.push(args[i + 1]); });
  return vals.length ? vals : def;
};
const starts = opt('start', []);
if (!starts.length) {
  console.error('Usage: node crawl-site.mjs --start https://www.example.org/ [--max 2000] [--out audit] [--http]');
  process.exit(1);
}
const MAX = Number(opt('max', ['2000'])[0]);
const DELAY = Number(opt('delay', ['400'])[0]);
const OUT = opt('out', ['audit'])[0];
const FORCE_HTTP = args.includes('--http');
const baseHost = (h) => h.replace(/^www\./, '');
const HOSTS = new Set([...opt('host', []), ...starts.map((s) => new URL(s).hostname)].map(baseHost));
const UA = 'Mozilla/5.0 (compatible; site-migration-audit/1.0; read-only)';

mkdirSync(join(OUT, 'pages'), { recursive: true });

const norm = (u) => {
  try {
    const x = new URL(u);
    x.hash = '';
    if (FORCE_HTTP && x.protocol === 'https:') x.protocol = 'http:';
    // Session/tracking parameters create endless duplicates.
    for (const k of [...x.searchParams.keys()]) if (/^(utm_|fbclid|gclid|sid|session|PHPSESSID)/i.test(k)) x.searchParams.delete(k);
    return x.toString();
  } catch {
    return null;
  }
};
const sameSite = (u) => HOSTS.has(baseHost(u.hostname));
const isAsset = (p) => /\.(jpe?g|png|gif|webp|avif|svg|pdf|docx?|pptx?|xlsx?|mp3|mp4|mov|zip|css|js|ico|woff2?|ttf)$/i.test(p);
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
const attr = (tag, name) => {
  const m = tag.match(new RegExp(`${name}\\s*=\\s*("([^"]*)"|'([^']*)'|([^\\s>]+))`, 'i'));
  return m ? (m[2] ?? m[3] ?? m[4] ?? '') : null;
};
const decode = (s) => s.replace(/&nbsp;/g, ' ').replace(/&amp;/g, '&').replace(/&#0?39;|&rsquo;|&lsquo;/g, "'")
  .replace(/&quot;|&ldquo;|&rdquo;/g, '"').replace(/&ndash;|&mdash;/g, '-').replace(/&lt;/g, '<').replace(/&gt;/g, '>');
const text = (h) => decode(h.replace(/<script[\s\S]*?<\/script>/gi, ' ').replace(/<style[\s\S]*?<\/style>/gi, ' ').replace(/<[^>]+>/g, ' ')).replace(/\s+/g, ' ').trim();

const queue = starts.map(norm);
const seen = new Set();
const pages = [];
const assets = new Map();
const external = new Map();

while (queue.length && pages.length < MAX) {
  const url = norm(queue.shift());
  if (!url || seen.has(url)) continue;
  seen.add(url);
  const u = new URL(url);
  if (!sameSite(u) || isAsset(u.pathname)) continue;
  let res;
  let html = '';
  try {
    res = await fetch(url, { redirect: 'manual', headers: { 'User-Agent': UA }, signal: AbortSignal.timeout(30000) });
    if (res.status >= 300 && res.status < 400) {
      const loc = res.headers.get('location');
      pages.push({ url, status: res.status, redirect: loc });
      if (loc) queue.push(new URL(loc, url).toString());
      continue;
    }
    const type = res.headers.get('content-type') || '';
    if (!/html/i.test(type)) {
      pages.push({ url, status: res.status, contentType: type });
      continue;
    }
    html = await res.text();
  } catch (e) {
    pages.push({ url, status: 'ERR', error: String(e.message || e) });
    continue;
  }
  const title = decode((html.match(/<title[^>]*>([\s\S]*?)<\/title>/i)?.[1] || '').trim());
  const desc = attr(html.match(/<meta[^>]+name=["']description["'][^>]*>/i)?.[0] || '', 'content');
  const h1 = text(html.match(/<h1[^>]*>([\s\S]*?)<\/h1>/i)?.[1] || '');
  const file = createHash('sha1').update(url).digest('hex').slice(0, 12) + '.html';
  writeFileSync(join(OUT, 'pages', file), html);
  const links = [];
  for (const m of html.matchAll(/<a\b[^>]*>([\s\S]*?)<\/a>/gi)) {
    const href = attr(m[0], 'href');
    if (!href || /^(javascript:|#)/i.test(href)) continue;
    if (/^(mailto:|tel:)/i.test(href)) {
      links.push({ href, text: text(m[1]).slice(0, 80) });
      continue;
    }
    let abs;
    try {
      abs = new URL(href, url).toString();
    } catch {
      continue;
    }
    links.push({ href: abs, text: text(m[1]).slice(0, 80) });
    const h = new URL(abs);
    if (sameSite(h)) {
      if (isAsset(h.pathname)) assets.set(norm(abs), { type: 'link', from: url });
      else queue.push(abs);
    } else if (/^https?:/.test(h.protocol)) external.set(abs, (external.get(abs) || 0) + 1);
  }
  const imgs = [];
  for (const m of html.matchAll(/<img\b[^>]*>/gi)) {
    const src = attr(m[0], 'src');
    if (!src) continue;
    let abs;
    try {
      abs = new URL(src, url).toString();
    } catch {
      continue;
    }
    imgs.push({ src: abs, alt: attr(m[0], 'alt'), width: attr(m[0], 'width'), height: attr(m[0], 'height') });
    if (!assets.has(abs)) assets.set(abs, { type: 'img', from: url, alt: attr(m[0], 'alt') });
  }
  pages.push({ url, status: res.status, file, title, desc, h1, textLen: text(html).length, links, imgs });
  process.stdout.write(`${pages.length} ${res.status} ${url}\n`);
  await sleep(DELAY);
}

const result = {
  crawledAt: new Date().toISOString(),
  starts,
  hosts: [...HOSTS],
  pages,
  assets: [...assets].map(([url, v]) => ({ url, ...v })),
  external: [...external].map(([url, n]) => ({ url, n })).sort((a, b) => b.n - a.n),
  queueLeft: queue.length,
};
writeFileSync(join(OUT, 'crawl.json'), JSON.stringify(result, null, 2));

// Human summary for the content audit.
const ok = pages.filter((p) => p.status === 200 && p.file);
const sections = new Map();
for (const p of ok) {
  const seg = new URL(p.url).pathname.split('/').filter(Boolean).slice(0, 2).join('/') || '/';
  sections.set(seg, (sections.get(seg) || 0) + 1);
}
const titles = new Map();
for (const p of ok) titles.set(p.title, [...(titles.get(p.title) || []), p.url]);
const dupes = [...titles].filter(([t, us]) => t && us.length > 1).sort((a, b) => b[1].length - a[1].length).slice(0, 25);
const externalHosts = new Map();
for (const { url, n } of result.external) {
  const h = new URL(url).hostname;
  externalHosts.set(h, (externalHosts.get(h) || 0) + n);
}
const lines = [
  `# Crawl summary`,
  ``,
  `Crawled ${result.crawledAt} from ${starts.join(', ')}.`,
  ``,
  `| Measure | Count |`,
  `| --- | --- |`,
  `| HTML pages (200) | ${ok.length} |`,
  `| Redirects | ${pages.filter((p) => p.redirect).length} |`,
  `| Errors / non-200 | ${pages.filter((p) => p.status !== 200 && !p.redirect).length} |`,
  `| Same-site assets (images, PDFs, …) | ${assets.size} |`,
  `| External links (unique) | ${external.size} |`,
  `| URLs left in queue (raise --max) | ${queue.length} |`,
  ``,
  `## Pages by section`,
  ``,
  ...[...sections].sort((a, b) => b[1] - a[1]).slice(0, 40).map(([s, n]) => `- \`${s}\`: ${n}`),
  ``,
  `## Duplicate titles (possible duplicate or template pages)`,
  ``,
  ...(dupes.length ? dupes.map(([t, us]) => `- "${t}" × ${us.length}`) : ['- none']),
  ``,
  `## Pages with little text (< 400 characters)`,
  ``,
  ...ok.filter((p) => p.textLen < 400).slice(0, 40).map((p) => `- ${p.url} (${p.textLen})`),
  ``,
  `## Missing descriptions`,
  ``,
  `${ok.filter((p) => !p.desc).length} of ${ok.length} pages have no meta description.`,
  ``,
  `## External sites linked most`,
  ``,
  ...[...externalHosts].sort((a, b) => b[1] - a[1]).slice(0, 25).map(([h, n]) => `- ${h}: ${n}`),
  ``,
  `## Errors`,
  ``,
  ...pages.filter((p) => p.status !== 200 && !p.redirect).slice(0, 50).map((p) => `- ${p.status} ${p.url}${p.error ? ` (${p.error})` : ''}`),
];
writeFileSync(join(OUT, 'summary.md'), lines.join('\n') + '\n');
console.log(`done: ${ok.length} pages, ${assets.size} assets, ${external.size} external links, queue left ${queue.length}`);

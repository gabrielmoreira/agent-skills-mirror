#!/usr/bin/env node
// Find openly licensed photos on Wikimedia Commons (CC BY, CC BY-SA, CC0, public domain) with credits.
//
//   node find-cc-photos.mjs --query "lindy hop dancers" [--limit 30] [--out cc-candidates.json]
//        [--download <folder> --width 1600 --pick "0,3,7"]
//
// Writes candidates with title, author, license, license URL, source page and a thumbnail URL. With
// --download, saves the picked files (via Commons' resized thumbnails) and a credits.json to paste into
// the gallery entries and docs/image-inventory.md. Always show credit on the site.
import { mkdirSync, writeFileSync } from 'node:fs';
import { join } from 'node:path';

const args = process.argv.slice(2);
const get = (k, d) => {
  const i = args.indexOf(`--${k}`);
  return i >= 0 ? args[i + 1] : d;
};
const query = get('query');
if (!query) {
  console.error('Usage: node find-cc-photos.mjs --query "swing dancers" [--limit 30] [--out file.json] [--download dir --pick "0,2"]');
  process.exit(1);
}
const limit = Number(get('limit', '30'));
const out = get('out', 'cc-candidates.json');
const width = Number(get('width', '1600'));
const UA = 'community-site-kit/1.0 (https://github.com/michaelsrichter/community-site-kit)';
const OK = /^(CC BY(-SA)? [\d.]+|CC0|Public domain|PD)/i;
const strip = (s) => String(s ?? '').replace(/<[^>]+>/g, '').replace(/\s+/g, ' ').trim();

const api = new URL('https://commons.wikimedia.org/w/api.php');
Object.entries({
  action: 'query', format: 'json', origin: '*', generator: 'search', gsrnamespace: '6', gsrlimit: String(Math.min(limit * 2, 100)),
  gsrsearch: `${query} filetype:bitmap`, prop: 'imageinfo', iiprop: 'url|extmetadata|size', iiurlwidth: '400',
}).forEach(([k, v]) => api.searchParams.set(k, v));
const json = await (await fetch(api, { headers: { 'User-Agent': UA } })).json();
const pages = Object.values(json.query?.pages ?? {}).sort((a, b) => (a.index ?? 0) - (b.index ?? 0));
const results = [];
for (const p of pages) {
  const ii = p.imageinfo?.[0];
  const m = ii?.extmetadata ?? {};
  const license = strip(m.LicenseShortName?.value);
  if (!ii || !OK.test(license)) continue;
  results.push({
    i: results.length,
    title: p.title,
    author: strip(m.Artist?.value) || 'Unknown',
    license,
    licenseUrl: m.LicenseUrl?.value ?? '',
    source: ii.descriptionurl,
    width: ii.width,
    height: ii.height,
    thumb: ii.thumburl,
    description: strip(m.ImageDescription?.value).slice(0, 200),
  });
  if (results.length >= limit) break;
}
writeFileSync(out, JSON.stringify(results, null, 2));
for (const r of results) console.log(`${r.i}. ${r.title.replace(/^File:/, '')} — ${r.author} — ${r.license} (${r.width}×${r.height})`);
console.log(`${results.length} openly licensed candidates → ${out}. Look at the thumbnails before choosing.`);

const dl = get('download');
if (dl) {
  const pickIdx = (get('pick', '') || '').split(',').filter(Boolean).map(Number);
  const chosen = pickIdx.length ? pickIdx.map((i) => results[i]).filter(Boolean) : results;
  mkdirSync(dl, { recursive: true });
  const credits = [];
  for (const r of chosen) {
    const u = new URL('https://commons.wikimedia.org/w/api.php');
    Object.entries({ action: 'query', format: 'json', origin: '*', titles: r.title, prop: 'imageinfo', iiprop: 'url', iiurlwidth: String(Math.min(width, r.width)) }).forEach(([k, v]) => u.searchParams.set(k, v));
    const info = Object.values((await (await fetch(u, { headers: { 'User-Agent': UA } })).json()).query.pages)[0].imageinfo[0];
    const buf = Buffer.from(await (await fetch(info.thumburl, { headers: { 'User-Agent': UA } })).arrayBuffer());
    const name = r.title.replace(/^File:/, '').replace(/\.[^.]+$/, '').toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '').slice(0, 60) + '.jpg';
    writeFileSync(join(dl, name), buf);
    credits.push({ file: name, credit: `Photo: ${r.author}, ${r.license}, via Wikimedia Commons`, creditUrl: r.source, licenseUrl: r.licenseUrl });
    console.log(`saved ${name}`);
  }
  writeFileSync(join(dl, 'credits.json'), JSON.stringify(credits, null, 2));
  console.log(`${credits.length} file(s) + credits.json → ${dl}. Strip metadata with prepare-photos.mjs before committing.`);
}

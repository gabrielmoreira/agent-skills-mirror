#!/usr/bin/env node
// Build a numbered contact sheet (grid of thumbnails) so a person or an AI can pick photos visually.
//
//   node contact-sheet.mjs --dir "<photo folder>" --out sheet.png [--cols 6] [--size 260] [--start 0] [--count 48] [--newest-first]
//
// Labels are the index used by prepare-photos.mjs --pick (zero-padded, in the same sort order).
// Also writes <out>.json with the index → file mapping. Needs `sharp` resolvable from the current folder.
import { readdirSync, readFileSync, statSync, writeFileSync } from 'node:fs';
import { join } from 'node:path';
import { createRequire } from 'node:module';

const require = createRequire(join(process.cwd(), 'package.json'));
const sharp = require('sharp');
const args = process.argv.slice(2);
const get = (k, d) => {
  const i = args.indexOf(`--${k}`);
  return i >= 0 ? args[i + 1] : d;
};
const dir = get('dir');
if (!dir) {
  console.error('Usage: node contact-sheet.mjs --dir <folder> --out sheet.png [--cols 6] [--size 260] [--start 0] [--count 48] [--newest-first]');
  process.exit(1);
}
const out = get('out', 'sheet.png');
const cols = Number(get('cols', '6'));
const size = Number(get('size', '260'));
const start = Number(get('start', '0'));
const count = Number(get('count', '48'));

export function listPhotos(folder, newestFirst) {
  const files = readdirSync(folder)
    .filter((f) => /\.(jpe?g|png|webp|heic|avif|tiff?)$/i.test(f))
    .map((f) => ({ f, t: statSync(join(folder, f)).mtimeMs }));
  files.sort(newestFirst ? (a, b) => b.t - a.t || a.f.localeCompare(b.f) : (a, b) => a.f.localeCompare(b.f));
  return files.map((x) => x.f);
}

const all = listPhotos(dir, args.includes('--newest-first'));
const pick = all.slice(start, start + count);
const pad = String(all.length - 1).length;
const label = 28;
const rows = Math.ceil(pick.length / cols);
const tiles = [];
const index = {};
for (const [k, f] of pick.entries()) {
  const n = String(start + k).padStart(pad, '0');
  index[n] = f;
  let thumb;
  try {
    thumb = await sharp(readFileSync(join(dir, f))).rotate().resize(size, size, { fit: 'contain', background: '#222' }).toBuffer();
  } catch (e) {
    console.warn(`skip ${f}: ${e.message}`);
    thumb = await sharp({ create: { width: size, height: size, channels: 3, background: '#550000' } }).png().toBuffer();
  }
  const caption = Buffer.from(
    `<svg width="${size}" height="${label}" xmlns="http://www.w3.org/2000/svg"><rect width="100%" height="100%" fill="#111"/><text x="8" y="20" font-family="Arial" font-size="16" fill="#fff">${n}  ${f.replace(/&/g, '&amp;').replace(/</g, '&lt;').slice(0, 26)}</text></svg>`,
  );
  const x = (k % cols) * size;
  const y = Math.floor(k / cols) * (size + label);
  tiles.push({ input: thumb, left: x, top: y }, { input: caption, left: x, top: y + size });
}
await sharp({ create: { width: cols * size, height: rows * (size + label), channels: 3, background: '#000' } })
  .composite(tiles)
  .png()
  .toFile(out);
writeFileSync(out.replace(/\.\w+$/, '') + '.json', JSON.stringify({ dir, order: args.includes('--newest-first') ? 'newest-first' : 'name', index }, null, 2));
console.log(`${pick.length} of ${all.length} photos → ${out} (indexes ${start}–${start + pick.length - 1})`);

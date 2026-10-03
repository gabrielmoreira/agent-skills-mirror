#!/usr/bin/env node
// Prepare photos for the web: auto-rotate, strip all metadata (EXIF/GPS), resize (never upscale), mozjpeg.
//
//   node prepare-photos.mjs --in "<photo folder>" --out src/assets/uploads/album [--pick "3,07,12"] \
//        [--newest-first] [--max 1600] [--quality 82] [--prefix lodge]
//
// --pick uses the indexes printed on a contact sheet (same sort order flags). Without --pick, all photos.
// Reads each file fully into memory first (Windows keeps sharp's file handles open otherwise).
import { mkdirSync, readdirSync, readFileSync, statSync, writeFileSync } from 'node:fs';
import { join, parse } from 'node:path';
import { createRequire } from 'node:module';

const require = createRequire(join(process.cwd(), 'package.json'));
const sharp = require('sharp');
const args = process.argv.slice(2);
const get = (k, d) => {
  const i = args.indexOf(`--${k}`);
  return i >= 0 ? args[i + 1] : d;
};
const input = get('in');
const out = get('out');
if (!input || !out) {
  console.error('Usage: node prepare-photos.mjs --in <folder> --out <folder> [--pick "1,2"] [--newest-first] [--max 1600] [--prefix name]');
  process.exit(1);
}
const max = Number(get('max', '1600'));
const quality = Number(get('quality', '82'));
const prefix = get('prefix', '');
const slug = (s) => s.toLowerCase().normalize('NFKD').replace(/[^\w\s-]/g, '').trim().replace(/[\s_]+/g, '-').replace(/-+/g, '-');

const files = readdirSync(input)
  .filter((f) => /\.(jpe?g|png|webp|heic|avif|tiff?)$/i.test(f))
  .map((f) => ({ f, t: statSync(join(input, f)).mtimeMs }));
files.sort(args.includes('--newest-first') ? (a, b) => b.t - a.t || a.f.localeCompare(b.f) : (a, b) => a.f.localeCompare(b.f));
const names = files.map((x) => x.f);
const pick = get('pick');
const chosen = pick ? pick.split(',').map((s) => names[Number(s.trim())]).filter(Boolean) : names;

mkdirSync(out, { recursive: true });
let total = 0;
for (const [k, f] of chosen.entries()) {
  const buf = readFileSync(join(input, f));
  const img = sharp(buf).rotate();
  const meta = await img.metadata();
  const longest = Math.max(meta.width ?? 0, meta.height ?? 0);
  const resized = longest > max ? img.resize({ width: meta.width >= meta.height ? max : undefined, height: meta.height > meta.width ? max : undefined, withoutEnlargement: true }) : img;
  const data = await resized.jpeg({ quality, mozjpeg: true }).toBuffer(); // no withMetadata(): EXIF/GPS stripped
  const name = `${prefix ? `${slug(prefix)}-` : ''}${slug(parse(f).name) || `photo-${k + 1}`}.jpg`;
  writeFileSync(join(out, name), data);
  const m2 = await sharp(data).metadata();
  total += data.length;
  console.log(`${f} → ${name}  ${m2.width}×${m2.height}  ${Math.round(data.length / 1024)} KB`);
}
console.log(`${chosen.length} photo(s), ${Math.round(total / 1024)} KB total → ${out}`);

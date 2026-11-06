#!/usr/bin/env node
// Illustration library of a style: every generated illustration lives ONCE in <profile>/styles/<style>/illustrations/library/,
// so any short of that style can reuse it. The engine reads a spec's assets/images/<name>.png there when the project has
// no such file; on macOS/Linux the project also gets a relative symlink (browsable, read by other tools).
//   node library.mjs import <project>...        move the project's assets/images files into its style's library
//                                               (dedup by content; a name taken by another image -> <name>-<slug>),
//                                               link them back, archive the sub-folders (raw renders) in library/raw/<slug>/
//   node library.mjs link <project> <name>[=<as>]...   use library images in a short as assets/images/<as>.<ext>
//   node library.mjs list [query] [--style <name>]     name, uses, prompt (default style of the profile without --style)
// library/index.json (name -> file, prompt, ar, refs, used by) and library/index.html (gallery) are rewritten each time.
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import crypto from 'node:crypto';

const argv = process.argv.slice(2);
const opt = k => { const i = argv.indexOf(`--${k}`); if (i < 0) return null; const v = argv[i + 1]; argv.splice(i, 2); return v; };
const STYLE_FLAG = opt('style');
const [cmd, ...args] = argv;
const IMG = /\.(png|jpe?g|webp)$/i;
const expand = p => p.replace(/^~/, os.homedir());
const readJSON = f => { try { return JSON.parse(fs.readFileSync(f, 'utf8')); } catch { return null; } };
const sha = f => crypto.createHash('sha1').update(fs.readFileSync(f)).digest('hex').slice(0, 16);
const slugOf = proj => path.basename(proj).replace(/^short-/, '');

// profile (LOCAL only): $SHORT_EDITING_HOME, else the nearest .short-editing/ in the start folder or a parent, home excluded
const HOME = start => expand(process.env.SHORT_EDITING_HOME || (s => { for (let d = s; d !== path.dirname(d); d = path.dirname(d)) if (d !== os.homedir() && fs.existsSync(path.join(d, '.short-editing'))) return path.join(d, '.short-editing'); return path.join(s, '.short-editing'); })(path.resolve(start)));
function styleDir(home, name) {
  const dir = path.join(home, 'styles');
  if (!name) { const d = readJSON(path.join(home, 'style.json'))?.default; if (typeof d === 'string') return path.join(dir, d); throw new Error(`no default style in ${home}/style.json, pass --style <name>`); }
  const low = String(name).toLowerCase();
  const d = fs.existsSync(dir) && fs.readdirSync(dir).map(n => path.join(dir, n)).find(d => path.basename(d).toLowerCase() === low || String(readJSON(path.join(d, 'style.json'))?.name || '').toLowerCase() === low);
  if (!d) throw new Error(`no style "${name}" in ${dir}`);
  return d;
}
const libOf = sdir => { const d = path.join(sdir, 'illustrations/library'); fs.mkdirSync(path.join(d, 'raw'), { recursive: true }); return fs.realpathSync(d); };
const projLib = proj => libOf(styleDir(HOME(proj), STYLE_FLAG || readJSON(path.join(proj, 'source/style.json'))?.name));

const load = lib => readJSON(path.join(lib, 'index.json'))?.items || {};
function save(lib, items) {
  const sorted = Object.fromEntries(Object.entries(items).sort(([a], [b]) => a.localeCompare(b)));
  fs.writeFileSync(path.join(lib, 'index.json'), JSON.stringify({ about: 'Illustrations of this style. name -> file, sha, prompt, ar, refs, used: [<short>/<name in the short>]. Written by short-editing/engine/library.mjs.', items: sorted }, null, 1) + '\n');
  const esc = s => String(s).replace(/[&<>"]/g, c => `&#${c.charCodeAt(0)};`);
  const card = ([n, it]) => `<figure title="${esc(it.prompt || '')}"><img loading="lazy" src="${esc(it.file)}"><figcaption><b>${esc(n)}</b><br>${esc((it.used || []).map(u => u.split('/')[0]).join(', '))}</figcaption></figure>`;
  fs.writeFileSync(path.join(lib, 'index.html'), `<!doctype html><meta charset="utf-8"><title>Illustrations (${Object.keys(sorted).length})</title><style>body{font:13px system-ui;background:#F7F7F5;margin:20px}main{display:grid;grid-template-columns:repeat(auto-fill,minmax(180px,1fr));gap:14px}figure{margin:0;background:#fff;border:1px solid #ddd;padding:8px}img{width:100%;height:170px;object-fit:contain}figcaption{color:#555}b{color:#111}input{font-size:16px;padding:6px;width:300px;margin-bottom:14px}</style><input placeholder="filter" oninput="for(const f of document.querySelectorAll('figure'))f.hidden=!(f.textContent+f.title).toLowerCase().includes(this.value.toLowerCase())"><main>${Object.entries(sorted).map(card).join('')}</main>\n`);
}

// a relative symlink; false where the system refuses it (Windows without developer mode): the engine reads the library then
function linkTo(link, target) {
  fs.rmSync(link, { force: true });
  try { fs.symlinkSync(path.relative(path.dirname(link), target), link); return true; } catch { return false; }
}
// without a symlink, a renamed image is renamed in the spec too
function renameInSpec(proj, from, to) {
  const f = path.join(proj, 'source/spec.js');
  if (from === to || !fs.existsSync(f)) return;
  const s = fs.readFileSync(f, 'utf8'), next = s.split(`assets/images/${from}`).join(`assets/images/${to}`);
  if (next !== s) fs.writeFileSync(f, next);
}

// prompts of a project: files/*prompts*.json (later versions win), then the manifests images.mjs wrote in the image folders
function prompts(proj) {
  const out = {}, put = o => { if (!o?.name) return; for (const k of ['prompt', 'ar', 'refs']) if (o[k]) (out[o.name] ??= {})[k] = o[k]; };
  const files = path.join(proj, 'files'), img = path.join(proj, 'assets/images');
  if (fs.existsSync(files)) for (const f of fs.readdirSync(files).filter(f => /prompts.*\.json$/.test(f)).sort()) [].concat(readJSON(path.join(files, f)) || []).forEach(put);
  const manifests = d => [path.join(d, 'manifest.json'), ...(fs.existsSync(d) ? fs.readdirSync(d, { withFileTypes: true }).filter(e => e.isDirectory()).map(e => path.join(d, e.name, 'manifest.json')) : [])];
  for (const m of manifests(img).filter(fs.existsSync).sort()) (readJSON(m)?.images || []).forEach(put);
  return out;
}

// move src into dst, merging folders (a file already there is replaced)
function moveInto(src, dst) {
  if (fs.lstatSync(src).isDirectory()) { fs.mkdirSync(dst, { recursive: true }); for (const e of fs.readdirSync(src)) moveInto(path.join(src, e), path.join(dst, e)); fs.rmdirSync(src); }
  else { fs.rmSync(dst, { force: true }); fs.renameSync(src, dst); }
}

function importProject(proj) {
  proj = path.resolve(expand(proj));
  const lib = projLib(proj), items = load(lib), slug = slugOf(proj), img = path.join(proj, 'assets/images'), P = prompts(proj), bySha = {};
  if (!fs.existsSync(img)) { console.log(`${slug}: no assets/images`); return; }
  for (const [n, it] of Object.entries(items)) bySha[it.sha] = n;
  let added = 0, known = 0;
  for (const f of fs.readdirSync(img)) {
    const src = path.join(img, f), st = fs.lstatSync(src);
    if (st.isDirectory()) { moveInto(src, path.join(lib, 'raw', slug, f)); continue; }
    if (st.isSymbolicLink() || !IMG.test(f)) continue;
    const h = sha(src), as = f.replace(IMG, ''), ext = path.extname(f);
    let name = bySha[h];
    if (name) { known++; fs.rmSync(src); }
    else {
      name = as;
      for (let i = 2; items[name] || fs.existsSync(path.join(lib, name + ext)); i++) name = i === 2 ? `${as}-${slug}` : `${as}-${slug}-${i}`;
      fs.renameSync(src, path.join(lib, name + ext));
      items[name] = { file: name + ext, sha: h, from: slug, created: st.mtime.toISOString().slice(0, 10), ...P[as], used: [] };
      bySha[h] = name; added++;
    }
    const file = items[name].file;
    if (!linkTo(src, path.join(lib, file))) renameInSpec(proj, f, file);
    items[name].used = [...new Set([...(items[name].used || []), `${slug}/${as}`])];
  }
  save(lib, items);
  console.log(`${slug}: ${added} added, ${known} already there -> ${lib} (${Object.keys(items).length} illustrations)`);
}

function link(proj, specs) {
  proj = path.resolve(expand(proj));
  const lib = projLib(proj), items = load(lib), slug = slugOf(proj), img = path.join(proj, 'assets/images');
  fs.mkdirSync(img, { recursive: true });
  for (const s of specs) {
    const [name, as = name] = s.split('='), it = items[name];
    if (!it) { console.error(`not in the library: ${name}`); process.exitCode = 1; continue; }
    const ext = path.extname(it.file), ok = linkTo(path.join(img, as + ext), path.join(lib, it.file));
    if (!ok && as !== name) { console.error(`${as}: no symlink on this system, use assets/images/${it.file} in the spec`); process.exitCode = 1; continue; }
    it.used = [...new Set([...(it.used || []), `${slug}/${as}`])];
    console.log(`${slug}: assets/images/${as}${ext}${ok ? ` -> ${it.file}` : ' (read from the library by the engine)'}`);
  }
  save(lib, items);
}

if (cmd === 'import' && args.length) args.forEach(importProject);
else if (cmd === 'link' && args.length > 1) link(args[0], args.slice(1));
else if (cmd === 'list') {
  const lib = libOf(styleDir(HOME(process.cwd()), STYLE_FLAG)), q = (args[0] || '').toLowerCase(), items = load(lib);
  for (const [n, it] of Object.entries(items)) if (!q || `${n} ${it.prompt || ''}`.toLowerCase().includes(q)) console.log(`${n.padEnd(28)} ${String((it.used || []).length).padStart(2)}x  ${(it.prompt || '').slice(0, 110)}`);
  console.log(`${Object.keys(items).length} illustrations, gallery: ${path.join(lib, 'index.html')}`);
}
else { console.error('usage: library.mjs import <project>... | link <project> <name>[=<as>]... | list [query]   [--style <name>]'); process.exit(1); }

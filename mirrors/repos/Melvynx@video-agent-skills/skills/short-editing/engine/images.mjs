#!/usr/bin/env node
// Image generation for shorts (B-roll stills, card illustrations, cutout backgrounds). One CLI, three providers:
//   codex   Codex CLI's built-in image_gen (free with a ChatGPT plan): one `codex exec` per image, the new file is
//           picked up from $CODEX_HOME/generated_images (same system as the codex-multiple-images-generations skill)
//   openai  Images API with OPENAI_API_KEY
//   gemini  Gemini image models with GEMINI_API_KEY
// The provider, model and the creator's image style come from the profile's default style (its style.json `images`),
// keys from the environment or $SHORT_EDITING_HOME/.env. The style suffix (and the palette) is appended to every
// prompt unless --raw.
//
//   node images.mjs --prompts '[{"name":"rocket","prompt":"..."}]' --out <dir> [--ar 2:3] [--provider codex]
//                   [--model m] [--concurrency 2] [--raw] [--dry-run]
//   node images.mjs --check            which providers work here (no generation)
// --prompts: JSON array (strings or {name, prompt, ar, refs}) or a file with one. refs (or --refs a.png,b.png) = local
// reference images (character sheets, a mascot drawing), all three providers: attached to the Codex job and passed to
// image_gen, sent as image parts before the prompt to Gemini, and to the OpenAI Images edits endpoint.
// --skip-existing keeps images already in --out (redo one = trash its file and rerun). --ar: 1:1, 2:3, 3:2, 9:16, 16:9 (default 2:3).
// Writes <out>/<name>.png|jpg and <out>/manifest.json, prints the file paths.
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { spawn, spawnSync } from 'node:child_process';
import { codexCmd } from './platform.mjs';

const argv = process.argv.slice(2);
const flag = (k, d) => { const i = argv.indexOf('--' + k); return i < 0 ? d : (argv[i + 1] && !argv[i + 1].startsWith('--') ? argv[i + 1] : true); };
const expand = p => p && path.resolve(String(p).replace(/^~(?=$|\/)/, os.homedir()));
// profile (LOCAL only): $SHORT_EDITING_HOME, else the nearest .short-editing/ in cwd or a parent, home folder excluded
const HOME = expand(process.env.SHORT_EDITING_HOME || (s => { for (let d = s; d !== path.dirname(d); d = path.dirname(d)) if (d !== os.homedir() && fs.existsSync(path.join(d, '.short-editing'))) return path.join(d, '.short-editing'); return path.join(s, '.short-editing'); })(process.cwd()));
const CODEX_HOME = expand(process.env.CODEX_HOME || '~/.codex'), GEN = path.join(CODEX_HOME, 'generated_images');
const log = (...a) => console.log(...a);
const slug = s => String(s).toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g, '').replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '').slice(0, 48) || 'image';
try { os.setPriority(0, 15); } catch {}

// the default style: <profile>/styles/<name>/ when <profile>/style.json only names it ({"default": "<name>"}), else that file
const read = f => { try { return JSON.parse(fs.readFileSync(f, 'utf8')); } catch { return {}; } };
const profile = (r => typeof r.default === 'string' ? read(path.join(HOME, 'styles', r.default, 'style.json')) : r)(read(path.join(HOME, 'style.json')));
const IMG = profile.images || {};
function key(...names) {
  for (const n of names) if (process.env[n]) return process.env[n];
  for (const env of [path.join(HOME, '.env'), path.join(os.homedir(), '.short-editing/.env')]) {   // keys only may be machine-wide
    if (!fs.existsSync(env)) continue;
    const txt = fs.readFileSync(env, 'utf8');
    for (const n of names) { const m = txt.match(new RegExp(`^\\s*(?:export\\s+)?${n}\\s*=\\s*["']?([^"'\\s#]+)`, 'm')); if (m) return m[1]; }
  }
  return null;
}
const [CODEX, CODEX_ARGS] = codexCmd();
const codexReady = () => spawnSync(CODEX, [...CODEX_ARGS, 'login', 'status'], { stdio: ['ignore', 'pipe', 'pipe'], encoding: 'utf8' }).status === 0;
const KEYS = { openai: () => key('OPENAI_API_KEY'), gemini: () => key('GEMINI_API_KEY', 'GOOGLE_API_KEY') };
const DEFAULT_MODEL = { openai: 'gpt-image-2.5-flare', gemini: 'gemini-3.1-flash-image' };

if (flag('check')) {
  const r = { codex: codexReady(), openai: !!KEYS.openai(), gemini: !!KEYS.gemini() };
  log(JSON.stringify({ profile: IMG.provider || null, available: r, pick: pickProvider(true) }, null, 2));
  process.exit(0);
}

function pickProvider(soft) {
  const want = flag('provider') !== undefined && flag('provider') !== true ? flag('provider') : IMG.provider;
  if (want === 'none') { if (soft) return 'none'; throw new Error('image generation is off in the profile (images.provider = none): run studio-setup to turn it on'); }
  if (want) return want;
  if (codexReady()) return 'codex';
  if (KEYS.openai()) return 'openai';
  if (KEYS.gemini()) return 'gemini';
  if (soft) return null;
  throw new Error(`no image provider: install and log in to Codex (codex login), or put OPENAI_API_KEY / GEMINI_API_KEY in ${path.join(HOME, '.env')}`);
}

// ---- prompts
function readPrompts() {
  const src = flag('prompts'); if (!src || src === true) throw new Error('--prompts <json|file> is required');
  const raw = String(src).trim().startsWith('[') ? src : fs.readFileSync(expand(src), 'utf8');
  const arr = JSON.parse(raw); if (!Array.isArray(arr) || !arr.length) throw new Error('--prompts must be a non-empty JSON array');
  const ar = flag('ar', '2:3'), seen = new Set();
  return arr.map((e, i) => {
    const o = typeof e === 'string' ? { prompt: e } : e;
    let name = slug(o.name || o.prompt.split(/\s+/).slice(0, 5).join(' '));
    while (seen.has(name)) name += '-' + (i + 1); seen.add(name);
    const refs = (o.refs || (typeof flag('refs') === 'string' ? flag('refs').split(',') : [])).map(expand);
    for (const r of refs) if (!fs.existsSync(r)) throw new Error(`reference image missing: ${r}`);
    return { name, prompt: o.prompt, ar: o.ar || ar, refs };
  });
}
// the creator's look: style text + palette, so generated stills sit on the paper like the rest of the short
function styled(p) {
  if (flag('raw')) return p;
  const c = profile.colors, parts = [p];
  if (IMG.style) parts.push(`Visual style: ${IMG.style}.`);
  if (c && IMG.palette !== false) parts.push(`Color palette: background close to ${c.paper || '#F1EEE6'}, ink ${c.ink || '#14161B'}, one accent ${c.accent || '#258EFF'}.`);
  parts.push('No text, no letters, no watermark, no logo unless asked.');
  return parts.join('\n');
}
const SIZE = { '1:1': '1024x1024', '2:3': '1024x1536', '3:2': '1536x1024', '9:16': '1024x1824', '16:9': '1824x1024' };
const MIME = { '.png': 'image/png', '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg', '.webp': 'image/webp' };
const mime = f => MIME[path.extname(f).toLowerCase()] || 'image/png';

// ---- providers: each returns { buf, ext }
async function openai(job, model) {
  const k = KEYS.openai(); if (!k) throw new Error(`OPENAI_API_KEY missing (env or ${path.join(HOME, '.env')})`);
  // refs go to the edits endpoint (multipart, one image[] per reference), plain prompts to generations
  let body = JSON.stringify({ model, prompt: job.full, size: SIZE[job.ar] || '1024x1536', n: 1 }), headers = { authorization: `Bearer ${k}`, 'content-type': 'application/json' };
  if (job.refs.length) {
    body = new FormData(); headers = { authorization: `Bearer ${k}` };
    for (const [f, v] of Object.entries({ model, prompt: job.full, size: SIZE[job.ar] || '1024x1536', n: '1' })) body.append(f, v);
    for (const r of job.refs) body.append('image[]', new Blob([fs.readFileSync(r)], { type: mime(r) }), path.basename(r));
  }
  const r = await fetch(`https://api.openai.com/v1/images/${job.refs.length ? 'edits' : 'generations'}`, { method: 'POST', headers, body, signal: AbortSignal.timeout(300000) });
  if (!r.ok) throw new Error(`OpenAI HTTP ${r.status}: ${(await r.text()).slice(0, 300)}`);
  const j = await r.json(), b = j.data?.[0]?.b64_json; if (!b) throw new Error('OpenAI returned no image');
  return { buf: Buffer.from(b, 'base64'), ext: '.png' };
}
async function gemini(job, model) {
  const k = KEYS.gemini(); if (!k) throw new Error(`GEMINI_API_KEY missing (env or ${path.join(HOME, '.env')})`);
  // current shape (v1, responseFormat.image) first, then the older v1beta imageConfig shape
  const bodies = [
    ['v1', { responseModalities: ['IMAGE'], responseFormat: { image: { aspectRatio: job.ar } } }],
    ['v1beta', { responseModalities: ['IMAGE'], imageConfig: { aspectRatio: job.ar } }],
  ];
  // refs ride along as image parts before the prompt (the model reads them as the character / style to keep)
  const parts = [...job.refs.map(f => ({ inlineData: { mimeType: mime(f), data: fs.readFileSync(f).toString('base64') } })), { text: job.full }];
  let last;
  for (const [ver, gc] of bodies) {
    const r = await fetch(`https://generativelanguage.googleapis.com/${ver}/models/${model}:generateContent`, {
      method: 'POST', headers: { 'x-goog-api-key': k, 'content-type': 'application/json' },
      body: JSON.stringify({ contents: [{ parts }], generationConfig: gc }), signal: AbortSignal.timeout(300000),
    });
    if (!r.ok) { last = `Gemini HTTP ${r.status}: ${(await r.text()).slice(0, 300)}`; if (r.status === 400 || r.status === 404) continue; throw new Error(last); }
    const j = await r.json(), part = (j.candidates?.[0]?.content?.parts || []).find(p => p.inlineData?.data);
    if (!part) throw new Error('Gemini returned no image (prompt blocked?)');
    return { buf: Buffer.from(part.inlineData.data, 'base64'), ext: part.inlineData.mimeType === 'image/jpeg' ? '.jpg' : '.png' };
  }
  throw new Error(last);
}
function listGen() {
  const out = new Map(); if (!fs.existsSync(GEN)) return out;
  const walk = d => { for (const e of fs.readdirSync(d, { withFileTypes: true })) { const f = path.join(d, e.name); if (e.isDirectory()) walk(f); else if (/\.(png|jpe?g|webp)$/i.test(e.name)) out.set(f, fs.statSync(f).mtimeMs); } };
  walk(GEN); return out;
}
async function codex(job, model, outDir) {
  const before = listGen(), t0 = Date.now();
  const prompt = ['You are running inside a batch image-generation automation.',
    'Use your built-in image_gen tool to generate exactly one raster image for the prompt below.',
    `Aspect ratio: ${job.ar} (${job.ar === '1:1' ? 'square' : +job.ar.split(':')[0] > +job.ar.split(':')[1] ? 'landscape' : 'portrait'}).`,
    ...(job.refs.length ? [`Reference images (attached, and on disk): ${job.refs.join(', ')}. Pass these exact absolute paths to image_gen as referenced_image_paths and follow them closely (same character, same drawing style).`] : []),
    'Do not edit or create any file. Do not ask follow-up questions. Do not generate SVG, HTML or placeholders.',
    'After generation reply with exactly: IMAGE_PATH: <absolute generated image path>', '', 'Image prompt:', job.full].join('\n');
  const args = ['--ask-for-approval', 'never', '--sandbox', 'read-only', 'exec', '--skip-git-repo-check', '--cd', outDir];
  if (model) args.push('--model', model);
  for (const r of job.refs) args.push(`--image=${r}`);
  args.push('-');
  const logF = path.join(outDir, 'logs', `${job.name}.log`); fs.mkdirSync(path.dirname(logF), { recursive: true });
  const text = await new Promise(res => {
    const ch = spawn(CODEX, [...CODEX_ARGS, ...args], { stdio: ['pipe', 'pipe', 'pipe'] }); let s = '';
    ch.stdout.on('data', b => s += b); ch.stderr.on('data', b => s += b);
    ch.on('error', e => res(s + '\nERROR ' + e.message)); ch.on('close', () => res(s));
    ch.stdin.end(prompt);   // closes stdin: codex exec reads it to EOF before starting
  });
  fs.writeFileSync(logF, text);
  const sid = text.match(/session id:\s*([0-9a-f-]+)/i)?.[1];
  const fresh = [...listGen()].filter(([f, m]) => !before.has(f) && m >= t0 - 5000);
  const reported = [...text.matchAll(/IMAGE_PATH:\s*(\S+\.(?:png|jpe?g|webp))/gi)].map(m => m[1]).filter(f => fs.existsSync(f));
  const pick = reported.at(-1) || fresh.filter(([f]) => sid && f.includes(sid)).map(([f]) => f).at(-1) || (fresh.length === 1 ? fresh[0][0] : null);
  if (!pick) throw new Error(`codex produced no image (log: ${logF})`);
  return { buf: fs.readFileSync(pick), ext: path.extname(pick).toLowerCase() };
}

// ---- run
// the profile model only goes with the profile provider (a --provider switch takes that provider's default model)
const provider = pickProvider(false), model = flag('model') !== undefined && flag('model') !== true ? flag('model') : (!IMG.provider || IMG.provider === provider) && IMG.model || DEFAULT_MODEL[provider];
const run = { codex, openai, gemini }[provider]; if (!run) throw new Error(`unknown provider ${provider} (codex, openai, gemini)`);
const jobs = readPrompts().map(j => ({ ...j, full: styled(j.prompt) }));
const outDir = expand(flag('out', 'images')); fs.mkdirSync(outDir, { recursive: true });
log(`images: ${jobs.length} with ${provider}${model ? ' ' + model : ''} -> ${outDir}`);
if (flag('dry-run')) { for (const j of jobs) log(`\n--- ${j.name} (${j.ar})\n${j.full}`); process.exit(0); }

const conc = Math.max(1, +flag('concurrency', provider === 'codex' ? 2 : 3)), results = [];
let next = 0;
await Promise.all(Array.from({ length: Math.min(conc, jobs.length) }, async () => {
  while (next < jobs.length) {
    const j = jobs[next++], t = Date.now();
    const done = flag('skip-existing') && ['.png', '.jpg', '.jpeg', '.webp'].map(e => path.join(outDir, j.name + e)).find(f => fs.existsSync(f));
    if (done) { results.push({ name: j.name, prompt: j.prompt, file: done, skipped: true }); log(`  skip ${done}`); continue; }
    try {
      const { buf, ext } = await run(j, model, outDir), file = path.join(outDir, j.name + ext);
      fs.writeFileSync(file, buf); results.push({ name: j.name, prompt: j.prompt, ar: j.ar, file, provider, model: model || null });
      log(`  ok ${file} (${((Date.now() - t) / 1000).toFixed(0)}s)`);
    } catch (e) { results.push({ name: j.name, prompt: j.prompt, error: e.message }); log(`  FAILED ${j.name}: ${e.message}`); }
  }
}));
fs.writeFileSync(path.join(outDir, 'manifest.json'), JSON.stringify({ createdAt: new Date().toISOString(), provider, model: model || null, images: results }, null, 2) + '\n');
const bad = results.filter(r => r.error).length;
log(`${results.length - bad}/${jobs.length} images, manifest ${path.join(outDir, 'manifest.json')}`);
process.exit(bad ? 1 : 0);

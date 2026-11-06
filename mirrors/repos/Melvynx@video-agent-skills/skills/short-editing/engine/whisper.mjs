// Word timestamps on this computer with whisper.cpp, free and offline: writes <project>/assets/words-scribe.json in the
// same shape as ElevenLabs Scribe ({language_code, text, words: [{text, start, end, type: 'word' | 'spacing'}]}, seconds),
// so `prepare` and everything after it work the same. `short.mjs words` calls it when no ElevenLabs key is set.
//   node whisper.mjs <project> [lang]        (also: node whisper.mjs --check, node whisper.mjs --model)
// whisper-cli: WHISPER_CLI, else <skill>/.runtime/whisper/ (setup.mjs on Windows), else the PATH (brew install whisper-cpp).
// Model: WHISPER_MODEL (a ggml name like small, medium, large-v3-turbo-q5_0, or a .bin path), default large-v3-turbo-q5_0
// (574 MB, about real time on a laptop); `small` (466 MB) is 2 to 3 times faster and mishears more names.
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { spawnSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';
import { FFMPEG, IS_WIN } from './platform.mjs';

const ENGINE = path.dirname(fileURLToPath(import.meta.url));
const SKILL = path.dirname(ENGINE);
export const MODEL_DIR = IS_WIN ? path.join(process.env.LOCALAPPDATA || os.tmpdir(), 'whisper-cpp') : path.join(os.homedir(), '.cache', 'whisper-cpp');
const exists = f => { try { return fs.existsSync(f); } catch { return false; } };

export function findWhisper() {
  if (process.env.WHISPER_CLI) return process.env.WHISPER_CLI;
  const local = path.join(SKILL, '.runtime', 'whisper');
  const walk = d => exists(d) ? fs.readdirSync(d, { withFileTypes: true }).flatMap(e => e.isDirectory() ? walk(path.join(d, e.name)) : [path.join(d, e.name)]) : [];
  const hit = walk(local).find(f => /^whisper-cli(\.exe)?$/.test(path.basename(f)));
  if (hit) return hit;
  for (const name of ['whisper-cli', 'whisper-cpp']) {
    const r = spawnSync(IS_WIN ? 'where' : 'which', [name], { encoding: 'utf8' });
    if (!r.status && r.stdout.trim()) return r.stdout.trim().split(/\r?\n/)[0];
  }
  return null;
}

export function modelPath() {
  const m = process.env.WHISPER_MODEL || 'large-v3-turbo-q5_0';
  return m.endsWith('.bin') ? path.resolve(m) : path.join(MODEL_DIR, `ggml-${m}.bin`);
}

// downloads the model once (Hugging Face, ggml-org), to a .part file renamed at the end
export async function ensureModel(log = console.log) {
  const file = modelPath();
  if (exists(file)) return file;
  const name = path.basename(file), url = `https://huggingface.co/ggerganov/whisper.cpp/resolve/main/${name}`;
  fs.mkdirSync(path.dirname(file), { recursive: true });
  log(`whisper: downloading ${name} (about 0.5 GB, once) -> ${path.dirname(file)}`);
  const r = await fetch(url);
  if (!r.ok) throw new Error(`model download failed: HTTP ${r.status} on ${url} (WHISPER_MODEL=small, medium or large-v3-turbo-q5_0)`);
  const total = +r.headers.get('content-length') || 0, part = file + '.part', out = fs.createWriteStream(part);
  let got = 0, shown = 0;
  for await (const chunk of r.body) {
    out.write(chunk); got += chunk.length;
    if (total && got / total - shown >= .1) { shown = got / total; log(`whisper: ${Math.round(shown * 100)} %`); }
  }
  await new Promise((ok, ko) => out.end(e => e ? ko(e) : ok()));
  fs.renameSync(part, file);
  return file;
}

// whisper.cpp tokens (sub-words with their own offsets) into words: a token starting with a space opens a new word
function toWords(json) {
  const words = [];
  for (const seg of json.transcription || []) for (const t of seg.tokens || []) {
    const text = t.text || '';
    if (!text.trim() || /^\[_.*_\]$/.test(text.trim()) || /^\[.*\]$/.test(text.trim())) continue;
    const from = t.offsets.from / 1000, to = t.offsets.to / 1000, last = words.at(-1);
    if (last && !/^\s/.test(text)) { last.text += text; last.end = Math.max(last.end, to); continue; }
    words.push({ text: text.trim(), start: from, end: Math.max(to, from + .02) });
  }
  // keep the timeline monotonic: a word never starts before the previous one ends
  for (let i = 1; i < words.length; i++) if (words[i].start < words[i - 1].end) words[i].start = Math.min(words[i - 1].end, words[i].end - .02);
  return words.filter(w => w.text);
}

// whisper drops repeats and false starts and spreads their time over the next words, so a retake
// becomes invisible. A prompt written with hesitations makes it transcribe what was really said.
const VERBATIM = {
  fr: "Euh, alors, j'ai, j'ai testé tous les, euh, tous les.",
  en: 'Um, so, I, I tried all the, uh, all the.',
  es: 'Eh, bueno, yo, yo probé todos los, eh, todos los.',
  de: 'Äh, also, ich, ich hab alle, äh, alle.',
  it: 'Ehm, allora, ho, ho provato tutti i, ehm, tutti i.',
  pt: 'Hum, então, eu, eu testei todos os, hum, todos os.',
};

export async function whisperWords(PROJ, lang, wav, log = console.log) {
  const cli = findWhisper();
  if (!cli) throw new Error(IS_WIN ? 'whisper.cpp not found: run node <skill>/engine/setup.mjs (it installs it)'
    : `whisper.cpp not found: ${process.platform === 'darwin' ? 'brew install whisper-cpp' : 'build whisper.cpp and put whisper-cli on the PATH'}, or set WHISPER_CLI`);
  const model = await ensureModel(log), t0 = Date.now();
  const tmp = fs.mkdtempSync(path.join(os.tmpdir(), 'whisper-')), w16 = path.join(tmp, 'a.wav');
  let r = spawnSync(FFMPEG, ['-v', 'error', '-y', '-i', wav, '-ac', '1', '-ar', '16000', '-c:a', 'pcm_s16le', w16]);
  if (r.status) throw new Error(`ffmpeg could not read ${wav}: ${String(r.stderr).slice(-300)}`);
  log(`whisper: transcribing on this computer (${path.basename(model)}, about real time)`);
  const threads = String(Math.max(2, Math.min(8, os.cpus().length)));
  r = spawnSync(cli, ['-m', model, '-f', w16, '-l', lang || 'auto', '-t', threads, '-ojf', '-of', path.join(tmp, 'out'), '-np',
    ...(VERBATIM[lang] ? ['--prompt', VERBATIM[lang]] : [])],
    { encoding: 'utf8', maxBuffer: 1 << 28 });
  if (r.status) throw new Error(`whisper-cli failed (${r.status}): ${(r.stderr || '').slice(-400)}`);
  const json = JSON.parse(fs.readFileSync(path.join(tmp, 'out.json'), 'utf8'));
  fs.rmSync(tmp, { recursive: true, force: true });
  const words = toWords(json);
  if (!words.length) throw new Error('transcription returned 0 words (silent audio? wrong language?)');
  const out = [];
  words.forEach((w, i) => { if (i) out.push({ text: ' ', start: words[i - 1].end, end: w.start, type: 'spacing' }); out.push({ ...w, type: 'word' }); });
  const res = { language_code: json.result?.language || lang || '', text: words.map(w => w.text).join(' '), words: out, source: 'whisper.cpp' };
  fs.writeFileSync(path.join(PROJ, 'assets/words-scribe.json'), JSON.stringify(res, null, 2));
  log(`words: ${words.length} words, lang ${res.language_code} (${((Date.now() - t0) / 1000).toFixed(1)}s, whisper.cpp) -> assets/words-scribe.json`);
  log('tip: an ElevenLabs key (ELEVENLABS_API_KEY in video-agent/.env) makes words use Scribe, which hears every retake and false start');
}

if (process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  const [a, lang] = process.argv.slice(2);
  if (a === '--check') { const c = findWhisper(); console.log(c ? `whisper-cli: ${c}\nmodel: ${modelPath()}${exists(modelPath()) ? '' : ' (not downloaded yet)'}` : 'whisper-cli: missing'); process.exit(c ? 0 : 1); }
  else if (a === '--model') await ensureModel();
  else if (!a) { console.error('usage: node whisper.mjs <project> [lang] | --check | --model'); process.exit(1); }
  else {
    const PROJ = path.resolve(a), wav = path.join(PROJ, 'assets/source.wav'), src = path.join(PROJ, 'assets/source.mp4');
    if (!exists(wav)) spawnSync(FFMPEG, ['-v', 'error', '-y', '-i', src, '-vn', '-ac', '1', '-ar', '48000', '-c:a', 'pcm_s16le', wav]);
    await whisperWords(PROJ, lang, wav);
  }
}

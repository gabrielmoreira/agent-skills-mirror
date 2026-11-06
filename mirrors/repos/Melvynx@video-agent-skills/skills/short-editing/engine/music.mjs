#!/usr/bin/env node
// Render procedural beds (lib/chill.js) to mp3: node music.mjs [style ... | --all] [--out <dir>] [--seed n]
// No style = the shorts library kept by ear (LIBRARY, picking guide in references/music.md), into ../assets/music by default.
// Prints length, loudness and the energy split per band, and keeps <out>/tracks.json (id, name, mood, bpm, desc, dur) in sync.
import fs from 'node:fs'; import path from 'node:path'; import { spawn } from 'node:child_process';
import { render, STYLES } from './lib/chill.js';
import { SR, SVF } from './lib/dsp.js';
import { FFMPEG } from './platform.mjs';

export const LIBRARY = ['enquete', 'arpege', 'filature', 'compte-a-rebours', 'sonar', 'code-noir', 'thriller', 'neon'];

const args = process.argv.slice(2), opt = k => { const i = args.indexOf(k); return i < 0 ? null : args.splice(i, 2)[1]; };
const all = args.includes('--all'); if (all) args.splice(args.indexOf('--all'), 1);
const out = path.resolve((opt('--out') || path.join(import.meta.dirname, '../assets/music')).replace(/^~/, process.env.HOME || process.env.USERPROFILE)), seed = +(opt('--seed') ?? 11);
const ids = all ? Object.keys(STYLES) : args.length ? args : LIBRARY;
for (const id of ids) if (!STYLES[id]) throw new Error(`unknown style ${id}: ${Object.keys(STYLES).join(', ')}`);
fs.mkdirSync(out, { recursive: true });

const encode = (file, L, R) => new Promise((ok, ko) => {
  const p = spawn(FFMPEG, ['-v', 'error', '-y', '-f', 'f32le', '-ar', String(SR), '-ac', '2', '-i', 'pipe:0', '-c:a', 'libmp3lame', '-b:a', '192k', file], { stdio: ['pipe', 'inherit', 'inherit'] });
  p.on('close', c => c ? ko(new Error(`ffmpeg exited ${c}`)) : ok());
  const I = new Float32Array(L.length * 2); for (let i = 0; i < L.length; i++) { I[2 * i] = L[i]; I[2 * i + 1] = R[i]; }
  p.stdin.end(Buffer.from(I.buffer));
});

const bands = (L, R) => { // % of energy below 150, 150-500, 500-2k, 2k-5k, above 5k Hz
  const cuts = [150, 500, 2000, 5000], F = cuts.map(() => new SVF()), E = new Float64Array(5);
  for (let i = 0; i < L.length; i++) {
    let x = (L[i] + R[i]) * .5;
    for (let j = 0; j < 4; j++) { F[j].run(x, cuts[j]); E[j] += F[j].lp * F[j].lp; x = F[j].hp; }
    E[4] += x * x;
  }
  const tot = E.reduce((a, b) => a + b, 0) || 1; return [...E].map(e => Math.round(e / tot * 100));
};

const meta = fs.existsSync(path.join(out, 'tracks.json')) ? Object.fromEntries(JSON.parse(fs.readFileSync(path.join(out, 'tracks.json'), 'utf8')).map(t => [t.id, t])) : {};
for (const id of ids) {
  const t0 = Date.now(), r = render(id, { seed }), ms = Date.now() - t0;
  let pk = 0; for (const X of [r.L, r.R]) for (let i = 0; i < X.length; i++) pk = Math.max(pk, Math.abs(X[i]));
  await encode(path.join(out, `${id}.mp3`), r.L, r.R);
  const st = STYLES[id]; meta[id] = { id, name: st.name, mood: st.mood, bpm: st.bpm, desc: st.desc, dur: +r.T.toFixed(1) };
  console.log(`[music] ${id.padEnd(13)} ${r.T.toFixed(1)}s ${r.bars} bars  ${r.lufs.toFixed(1)} LUFS  peak ${(20 * Math.log10(pk)).toFixed(1)} dB  bands ${bands(r.L, r.R).join('/')}%  ${(ms / 1000).toFixed(1)}s`);
}
fs.writeFileSync(path.join(out, 'tracks.json'), JSON.stringify(Object.keys(STYLES).filter(k => meta[k] && fs.existsSync(path.join(out, `${k}.mp3`))).map(k => meta[k]), null, 2) + '\n');
